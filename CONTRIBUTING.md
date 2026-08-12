# Contributing to WhatsMyName

Thanks for your interest in helping out! WhatsMyName is a community-maintained dataset, and it stays accurate because people like you report and fix site detections. Please also take a moment to read our [Code of Conduct](CODE_OF_CONDUCT.md).

## Two ways to help

**Don't want to touch JSON or GitHub?** [Submit a site via this form](https://forms.office.com/r/TscnNQqrD1), or [open an issue](https://github.com/WebBreacher/WhatsMyName/issues) with a link to an example profile. Someone else will do the implementation.

**Comfortable with JSON, HTTP, and a fork/pull-request workflow?** Add or fix a site entry yourself and submit a pull request. The rest of this document covers that path.

---

## The rules

These are the most common reasons a PR gets sent back for changes. Read them before you start, not after review.

1. **Capitalize the name the way the site does.** Visit the site and copy its own branding. If they write `PayPal`, the `name` field is `PayPal` -- not `paypal`, not `Paypal`.
2. **Order the fields the same way every entry does.** See [Field order](#field-order) below. This is what makes diffs fast to review; inconsistent ordering makes a one-line fix look like a rewrite. Note that our formatting bot only reorders fields after a PR merges, not during review, so get it right before you submit (see [Formatting and validation](#formatting-and-validation)).
3. **List at least two `known` accounts, and prefer well-established ones.** Pick accounts that are unlikely to be deleted or renamed -- popular, long-standing users are safer bets than accounts created for testing.
4. **Prefer GET over POST.** The project supports both, but GET is simpler to maintain and debug. Only use `post_body` when the site genuinely requires it.
5. **Make `e_string` and `m_string` truly unique.** Prefer a fragment of JSON or a distinctive piece of HTML (an id, a class name, a JSON key) over a plain phrase like `"joined at"`, which can appear on unrelated pages and cause false positives.
6. **Don't add new categories.** Use one of the existing values in the top-level `categories` array. If you think a genuinely new category is needed, open an issue to discuss it first rather than adding one in a data PR.
7. **First-time contributor? Add yourself to `authors`.** Add your name or handle to the `authors` array at the top of `wmn-data.json`. Welcome, and thank you.
8. **Validate your JSON before you submit.** Edit with a syntax-highlighting editor or JSON-aware IDE and fix anything it flags as invalid before opening the PR. See [Formatting and validation](#formatting-and-validation) for how to check this yourself.
9. **Keep PRs less than 10 sites.** If you have more additions, fixes, or removals than that, split them into separate PRs, or submit one and wait for it to be reviewed before opening the next. A single error in a 50-site PR can hold up 49 good changes.
10. **Remove entries for sites that are permanently gone**, rather than leaving a broken entry in place. If a site no longer meets the [inclusion criteria](README.md#how-it-works) (paywalled, login-only, or usernames no longer appear in the URL), remove it.

---

## Site entry format

`wmn-data.json` has three top-level elements: `license`, `authors`, and `sites`. You'll only ever touch `authors` (rule 7) and `sites`.

### Field order

Fields marked optional can be omitted, but when present, keep them in this order:

| Field | Required? | Purpose |
|---|---|---|
| `name` | required | Display name, capitalized per rule 1 |
| `uri_check` | required | URL to check, with `{account}` in place of the username |
| `uri_pretty` | optional | Human-readable profile URL, if `uri_check` is an API endpoint |
| `post_body` | optional | POST body content; if present, this entry is a POST request |
| `headers` | optional | HTTP headers to send; required if `post_body` is set |
| `strip_bad_char` | optional | Characters checking apps should strip from usernames first |
| `e_code` | required | HTTP status code for an account that exists |
| `e_string` | required | A unique string present only when the account exists (rule 5) |
| `m_string` | required | A unique string present only when the account does not exist (rule 5) |
| `m_code` | required | HTTP status code for an account that doesn't exist |
| `known` | required | At least two verified usernames for testing (rule 3) |
| `cat` | required | One of the existing values in the top-level `categories` array (rule 6) |
| `valid` | optional | Only set to `false` to tell checkers to skip a temporarily-broken site |
| `protection` | optional | Anti-automation measures present: `captcha`, `cloudflare`, `user-agent`, `user-auth`, etc. |

### Example: GET entry

```json
{
  "name": "Example GET",
  "uri_check": "https://www.example.com/load_profile_info.php?name={account}",
  "uri_pretty": "https://www.example.com/profile/{account}",
  "e_code": 200,
  "e_string": "\"registered_at\":",
  "m_string": "\"error\":\"not_found\"",
  "m_code": 404,
  "known": [
    "whoami",
    "johndoe"
  ],
  "cat": "images",
  "protection": [
    "captcha",
    "cloudflare"
  ],
  "headers": {
    "Accept": "text/html"
  }
}
```

### Example: POST entry

```json
{
  "name": "Example POST",
  "uri_check": "https://www.example.com/interact_api/load_profile_info.php",
  "post_body": "{\"username\":\"{account}\"}",
  "headers": {
    "Content-Type": "application/json"
  },
  "e_code": 200,
  "e_string": "\"registered_at\":",
  "m_string": "\"error\":\"not_found\"",
  "m_code": 404,
  "known": [
    "whoami",
    "johndoe"
  ],
  "cat": "images"
}
```

Note the header casing in both examples (`Accept`, `Content-Type`) -- HTTP header names are conventionally capitalized. Copy the case a browser's dev tools show you, and keep it consistent within an entry.

---

## Finding `e_code`, `m_code`, `e_string`, and `m_string`

So maybe you're wondering: how do I even find these things to add to the project? Good news -- it's mostly just comparing two web pages side by side, and you don't need to be a developer to do it.

Using a browser or a client like `curl`, request an existing profile and a profile you're confident doesn't exist, and compare the two responses:

```
# existing account
curl -i https://infosec.exchange/WebBreacher

# non-existing account
curl -i https://infosec.exchange/ThisDoesNotExistForSure504
```

- `e_code` / `m_code` are the HTTP status codes from each response. Don't assume 200/404 -- some sites return 200 for missing profiles, or 302 redirects.
- For `e_string` and `m_string`, look for a fragment that's on every matching page regardless of username. Per rule 5, prefer something structural (a JSON key, an HTML id or class) over ordinary text, and never include the username itself.

If you get stuck here, an issue with your example profile link is a perfectly good contribution on its own -- see [Two ways to help](#two-ways-to-help).

---

## Formatting and validation

- **Schema validation runs automatically on every PR** against [`wmn-data-schema.json`](wmn-data-schema.json) (via GitHub Actions). If it fails, check the workflow output for which field or entry it flagged.
- **The auto-sort/format bot does not run on your PR.** It only fires on pushes to branches in this repository, which for a fork-based PR means it applies after your change is merged, not before. Don't rely on it to fix your field order (rule 2) or alphabetize your entry -- do that yourself.
- **`sample.json`** is a small standalone file you can use to test a single entry against a checker tool without touching the full dataset. Replace its contents with your entry and run your checker of choice against it.

---

## Using AI tools

Feel free to leverage the power and attention to detail of AI systems to format, verify, and validate your changes before submitting -- checking JSON validity, comparing your entry against the rules above, or double-checking `e_string`/`m_string` uniqueness. If you do, please keep any AI-generated commentary in the PR description brief; we want a couple of sentences on what changed and why, not a lengthy AI-authored writeup.

---

## Submitting your PR

1. Confirm your JSON is valid and your entry follows the field order above.
2. Confirm `known` has at least two durable accounts (rule 3).
3. Keep the PR to fewer than 10 changed, added, or removed sites (rule 9). More than that, split it up.
4. If you're a first-time contributor, add yourself to `authors` (rule 7).
5. Open the pull request. GitHub will pre-fill the description with our PR template -- fill it out rather than deleting it (see below).

Someone will review, may ask for changes, and will merge once it looks right. Thanks again for helping keep the data accurate.

### Filling out the PR template

Every PR starts from [`.github/PULL_REQUEST_TEMPLATE.md`](.github/PULL_REQUEST_TEMPLATE.md). Here's what each part is actually asking for:

**Type of change** -- check the one box that describes this PR. If you're touching both a new site and a fix in the same PR, that's a sign the PR should probably be split (rule 9).

**Checklist (for new or updated site entries)** -- don't check a box you haven't actually done:
- The two `uri_check` boxes mean you ran the request yourself, once against a real account and once against one you're confident doesn't exist, and confirmed the codes and strings in your entry actually match what came back (see [Finding e_code, m_code, e_string, and m_string](#finding-e_code-m_code-e_string-and-m_string)).
- The `e_string`/`m_string` specificity box is rule 5 -- if the best you found is a generic phrase, keep looking before checking this.
- The public-access box is the [inclusion criteria](README.md#how-it-works): no login, no paywall, username visible in the URL.
- The JSON-valid box is rule 8. Note that despite what the checklist item says, auto-formatting does not run on your PR before review if you're contributing from a fork -- see [Formatting and validation](#formatting-and-validation). Validate it yourself first.

**Description** -- replace the comment with a couple of sentences: what site(s), what changed, and why (new addition, detection was broken, site is dead, etc.). This is what a reviewer reads before opening the diff, so a blank or one-word description slows review down.
