import json
import subprocess
import sys
import threading
from datetime import datetime, timezone
from pathlib import Path

from flask import Flask, jsonify, redirect, render_template, request, url_for

sys.path.insert(0, str(Path(__file__).parent))
from checker import load_sites, run_checker
from models import PROTECTION_TYPES

app = Flask(__name__)
app.secret_key = "wmn-checker-local"

REPO_ROOT = Path(__file__).parent.parent.parent
DATA_FILE = REPO_ROOT / "wmn-data.json"
SORT_SCRIPT = REPO_ROOT / "scripts" / "sort_format_json.py"
CACHE_FILE = Path(__file__).parent / "last_check.json"

_results: list = []
_progress: dict = {"total": 0, "done": 0, "complete": False, "running": False, "error": None, "run_started": None, "run_completed": None}
_lock = threading.Lock()


def _save_cache() -> None:
    try:
        payload = {
            "run_started": _progress.get("run_started"),
            "run_completed": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC"),
            "total": _progress.get("total", 0),
            "total_sites": _progress.get("total_sites", 0),
            "limit": _progress.get("limit"),
            "results": _results,
        }
        with open(CACHE_FILE, "w", encoding="utf-8") as f:
            json.dump(payload, f, indent=2, ensure_ascii=False)
    except Exception as exc:
        app.logger.warning("Could not save cache: %s", exc)


def _load_cache() -> None:
    if not CACHE_FILE.exists():
        return
    try:
        with open(CACHE_FILE, "r", encoding="utf-8") as f:
            payload = json.load(f)
        _results.extend(payload.get("results", []))
        checked = len([r for r in _results if r.get("checked_at")])
        total_sites = payload.get("total_sites", len(_results))
        _progress.update({
            "total": len(_results),
            "total_sites": total_sites,
            "remaining": max(0, total_sites - checked),
            "done": checked,
            "complete": True,
            "running": False,
            "run_started": payload.get("run_started"),
            "run_completed": payload.get("run_completed"),
            "limit": payload.get("limit"),
        })
    except Exception as exc:
        app.logger.warning("Could not load cache: %s", exc)


def _run_checker_thread(sites: list, limit: int) -> None:
    try:
        run_checker(sites, _results, _lock, _progress, limit=limit)
        _save_cache()
    except Exception as exc:
        with _lock:
            _progress["running"] = False
            _progress["complete"] = True
            _progress["error"] = str(exc)


with app.app_context():
    _load_cache()


@app.route("/")
def index():
    with _lock:
        results = list(_results)
        progress = dict(_progress)

    try:
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            _data = json.load(f)
        categories = sorted(_data.get("categories", []))
    except Exception:
        categories = sorted({r["cat"] for r in results if r.get("cat")})
    statuses = sorted({r["overall_status"] for r in results if r.get("overall_status")})

    return render_template(
        "results.html",
        results=results,
        progress=progress,
        categories=categories,
        statuses=statuses,
        protection_types=PROTECTION_TYPES,
    )


@app.route("/start", methods=["POST"])
def start_checker():
    limit_raw = request.form.get("limit", "").strip()
    limit = int(limit_raw) if limit_raw.isdigit() and int(limit_raw) > 0 else None

    with _lock:
        if _progress.get("running"):
            return redirect(url_for("index"))
        checked_names = {r["name"] for r in _results if r.get("checked_at")}
        _progress.update({
            "done": 0, "complete": False, "running": True, "error": None,
            "run_started": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC"),
            "run_completed": None,
            "limit": limit,
        })

    try:
        all_sites = load_sites(DATA_FILE)
    except Exception as exc:
        with _lock:
            _progress["running"] = False
            _progress["error"] = str(exc)
        return redirect(url_for("index"))

    remaining = [s for s in all_sites if s["name"] not in checked_names]
    with _lock:
        _progress["total_sites"] = len(all_sites)
        _progress["total"] = min(len(remaining), limit) if limit else len(remaining)
        _progress["remaining"] = len(remaining)

    t = threading.Thread(target=_run_checker_thread, args=(remaining, limit), daemon=True)
    t.start()
    return redirect(url_for("index"))


@app.route("/reset", methods=["POST"])
def reset_checker():
    with _lock:
        if _progress.get("running"):
            return redirect(url_for("index"))
        _results.clear()
        _progress.update({
            "total": 0, "total_sites": 0, "remaining": 0,
            "done": 0, "complete": False, "running": False,
            "error": None, "run_started": None, "run_completed": None, "limit": None,
        })
    if CACHE_FILE.exists():
        CACHE_FILE.unlink()
    return redirect(url_for("index"))


@app.route("/status")
def get_status():
    with _lock:
        return jsonify(dict(_progress))


@app.route("/save/<site_name>", methods=["POST"])
def save_site(site_name: str):
    try:
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)

        site = next((s for s in data["sites"] if s["name"] == site_name), None)
        if site is None:
            return jsonify({"success": False, "error": f"Site '{site_name}' not found"})

        # --- URI fields ---
        uri_check = request.form.get("uri_check", "").strip()
        if uri_check:
            site["uri_check"] = uri_check

        uri_pretty = request.form.get("uri_pretty", "").strip()
        if uri_pretty:
            site["uri_pretty"] = uri_pretty
        else:
            site.pop("uri_pretty", None)

        # --- Detection codes/strings ---
        for field in ("e_code", "m_code"):
            raw = request.form.get(field, "").strip()
            if raw:
                val = int(raw)
                if not (100 <= val <= 599):
                    raise ValueError(f"{field} {val} out of range 100-599")
                site[field] = val

        for field in ("e_string", "m_string"):
            val = request.form.get(field)
            if val is not None:
                site[field] = val

        # --- Known usernames ---
        known_raw = request.form.get("known", "")
        known = [u.strip() for u in known_raw.splitlines() if u.strip()]
        if known:
            site["known"] = known

        # --- Category ---
        cat = request.form.get("cat", "").strip()
        if cat:
            site["cat"] = cat

        # --- Optional fields: remove key if blank, set if provided ---
        strip_bad_char = request.form.get("strip_bad_char", "").strip()
        if strip_bad_char:
            site["strip_bad_char"] = strip_bad_char
        else:
            site.pop("strip_bad_char", None)

        post_body = request.form.get("post_body", "").strip()
        if post_body:
            site["post_body"] = post_body
        else:
            site.pop("post_body", None)

        headers_raw = request.form.get("headers", "").strip()
        if headers_raw:
            try:
                headers_parsed = json.loads(headers_raw)
                if not isinstance(headers_parsed, dict):
                    raise ValueError("headers must be a JSON object")
                site["headers"] = headers_parsed
            except json.JSONDecodeError as exc:
                raise ValueError(f"headers is not valid JSON: {exc}") from exc
        else:
            site.pop("headers", None)

        # --- valid field (3-state) ---
        valid_choice = request.form.get("valid", "absent")
        if valid_choice == "absent":
            site.pop("valid", None)
        elif valid_choice == "true":
            site["valid"] = True
        elif valid_choice == "false":
            site["valid"] = False

        # --- protection ---
        protection = request.form.getlist("protection")
        if protection:
            site["protection"] = protection
        else:
            site.pop("protection", None)

        with open(DATA_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

        proc = subprocess.run(
            [sys.executable, str(SORT_SCRIPT)],
            cwd=str(REPO_ROOT),
            capture_output=True,
            timeout=30,
        )
        if proc.returncode != 0:
            app.logger.warning("sort_format_json.py stderr: %s", proc.stderr.decode())

        # Sync in-memory result
        with _lock:
            for r in _results:
                if r["name"] == site_name:
                    r["uri_check"] = site["uri_check"]
                    r["uri_pretty"] = site.get("uri_pretty")
                    r["e_code"] = site["e_code"]
                    r["e_string"] = site["e_string"]
                    r["m_code"] = site["m_code"]
                    r["m_string"] = site["m_string"]
                    r["known"] = site["known"]
                    r["cat"] = site.get("cat", "")
                    r["valid_field"] = site.get("valid", None)
                    r["protection"] = site.get("protection", [])
                    r["has_protection"] = bool(site.get("protection"))
                    r["has_post_body"] = bool(site.get("post_body"))
                    break

        return jsonify({"success": True})

    except ValueError as exc:
        return jsonify({"success": False, "error": str(exc)})
    except Exception as exc:
        return jsonify({"success": False, "error": str(exc)})


@app.route("/recheck/<site_name>", methods=["POST"])
def recheck_site(site_name: str):
    try:
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)

        site = next((s for s in data["sites"] if s["name"] == site_name), None)
        if site is None:
            return jsonify({"success": False, "error": f"Site '{site_name}' not found"})

        import random
        from checker import check_site, UA_POOL
        from dataclasses import asdict
        ua = random.choice(UA_POOL)
        result = check_site(site, ua)
        result_dict = asdict(result)

        with _lock:
            for i, r in enumerate(_results):
                if r["name"] == site_name:
                    _results[i] = result_dict
                    break
            else:
                _results.append(result_dict)

        return jsonify({"success": True, "result": result_dict})

    except Exception as exc:
        return jsonify({"success": False, "error": str(exc)})


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=False)
