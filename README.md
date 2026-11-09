![WhatsMyName](whatsmyname.png)

# WhatsMyName

[![License: CC BY-SA 4.0](https://img.shields.io/badge/license-CC--BY--SA--4.0-lightgrey)](http://creativecommons.org/licenses/by-sa/4.0/)
[![Status: archived](https://img.shields.io/badge/status-archived-red)](#the-project-has-closed)
[![Sites](https://img.shields.io/badge/dynamic/json?url=https%3A%2F%2Fraw.githubusercontent.com%2FWebBreacher%2FWhatsMyName%2Fmain%2Fwmn-data.json&query=%24.sites.length&label=sites&color=blue)](wmn-data.json)
[![Contributors](https://img.shields.io/github/contributors/WebBreacher/WhatsMyName)](https://github.com/WebBreacher/WhatsMyName/graphs/contributors)

## The project has closed

**As of November 9, 2026, WhatsMyName is no longer maintained.** This repository is archived and read-only. Issues, pull requests and discussions are closed.

### Why I'm closing it

I started WhatsMyName in 2015 because I was frustrated with how inaccurate the username checker sites of the time were. Eleven years later, a few things have changed:

1. **My interests have moved on.** These days I spend my time on bookmarklets and other projects rather than on WhatsMyName.
2. **Maintenance has become too much.** Keeping hundreds of site detections working has fallen to me and a few others, and that's more than we can sustain.
3. **The problem it was built to solve has been solved.** There are some really neat username enumeration sites and tools now. WhatsMyName was a fix for a 2015 problem, and the field has caught up.

### Thank you

For eleven years, people used, forked, extended and argued about this project. Thank you to everyone who contributed a site or a fix, opened an issue, wrote a script or tool on top of the data, maintained a fork, taught it in a class, or used it in an investigation. WhatsMyName was only ever as good as the community around it, and that community made it better than I could have alone.

— Micah "WebBreacher" Hoffman

### What stays

The data stays here, and you can keep using it under its license:

- [`wmn-data.json`](wmn-data.json) holds the final dataset: 691 sites, last updated November 9, 2026.
- [`wmn-data-schema.json`](wmn-data-schema.json) is its JSON schema.
- Both stay at their current URLs, so tools that download them from `main` keep working.

Websites change all the time and nobody is updating these detections now, so the data will get less accurate over time. Treat results as leads to verify, not as facts.

## Table of Contents

- [About WhatsMyName](#about-whatsmyname)
- [How It Works](#how-it-works)
- [Data format](#data-format)
- [Tools and Sites That Use WhatsMyName](#tools-and-sites-that-use-whatsmyname)
- [License](#license)

---

## About WhatsMyName

WhatsMyName (WMN) was a community-maintained dataset for finding out whether a username exists across hundreds of websites. Investigators, researchers and curious people used it to verify online identities and check their own digital footprints.

[Micah "WebBreacher" Hoffman](https://webbreacher.com) created WhatsMyName in 2015 to deal with a real frustration: existing username checkers were full of false positives. Contributions from people all over the world grew it into one of the most widely used username enumeration datasets in the OSINT community.

Many tools and sites build on the data, and some have adopted the WhatsMyName name as well. Not all of them are connected to this project. The tools listed in [Tools and Sites That Use WhatsMyName](#tools-and-sites-that-use-whatsmyname) use WhatsMyName data and credit the project.

---

## How It Works

WMN is a single JSON file, `wmn-data.json`. Each entry describes how to check one website for a username: what URL to request, what a response looks like when the account exists, and what it looks like when it doesn't.

Tools read this file and do the actual checking. That separation means anyone can build a checker on top of the same data.

To be included, a site had to:

1. **Be publicly accessible.** Sites behind paywalls or logins can't be checked.
2. **Include the username in the URL.** The profile URL must contain the username directly.
3. **Not transform the username.** Sites that swap usernames for numeric IDs won't work.

---

## Data format

`wmn-data.json` has four top-level elements: `license`, `authors`, `categories` and `sites`. Each item in `sites` uses these fields, in this order:

| Field | Required? | Purpose |
|---|---|---|
| `name` | required | Display name of the site |
| `uri_check` | required | URL to check, with `{account}` in place of the username |
| `uri_pretty` | optional | Human-readable profile URL, used when `uri_check` is an API endpoint |
| `post_body` | optional | Request body. If present, the check is a POST request |
| `headers` | optional | HTTP headers to send. Always present when `post_body` is set |
| `strip_bad_char` | optional | Characters to remove from the username before building the request. Each character is removed separately (`"@."` means remove `@` and `.`) |
| `e_code` | required | HTTP status code when the account exists |
| `e_string` | required | A string present only when the account exists |
| `m_string` | required | A string present only when the account does not exist |
| `m_code` | required | HTTP status code when the account does not exist |
| `known` | required | Usernames that existed on the site when the entry was last verified |
| `cat` | required | Category, one of the values in the schema's `cat` enum |
| `valid` | optional | `false` means the entry was known to be broken. Checkers should skip it |
| `protection` | optional | Anti-automation measures seen on the site, such as `cloudflare`, `captcha` or `user-agent` |

### Checking a site

1. Remove any `strip_bad_char` characters from the username.
2. Replace `{account}` in `uri_check` (and in `post_body`, if present) with the username. Use plain string replacement: many `post_body` values are JSON, so template functions that treat `{` and `}` as placeholders will break them.
3. Send a POST with `post_body` and `headers` if `post_body` exists. Otherwise send a GET, still including any `headers`.
4. Decide the result:
   - **Found:** the status code equals `e_code` and the body contains `e_string`.
   - **Not found:** the status code equals `m_code` and the body contains `m_string`.
   - **Anything else** is unknown: the site may be blocking you, down, or changed since the entry was written.

Many sites use the same code for both outcomes (often `200`), so never decide on the status code alone. Always check the strings too.

### Example: GET entry

```json
{
  "name": "Example GET",
  "uri_check": "https://www.example.com/load_profile_info.php?name={account}",
  "uri_pretty": "https://www.example.com/profile/{account}",
  "headers": {
    "Accept": "text/html"
  },
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
  ]
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

---

## Tools and Sites That Use WhatsMyName

These tools used WhatsMyName data and credited the project as of November 2026. Their maintainers run them independently, and this list will not be updated.

### 🌐 Web-based (no install required)
| Tool | Type | Description |
|------|------|-------------|
| [whatsmyname.app](https://whatsmyname.app/) | ![Web](https://img.shields.io/badge/-Web-FF6F00) | The go-to web interface by [the OSINT Combine team](https://twitter.com/osintcombine). Filters by category, exports to CSV and PDF, always pulls the latest data. |
| [FreeUsername](https://freeusername.com/) | ![Web](https://img.shields.io/badge/-Web-FF6F00) | Formerly WhatsMyName Apps (independent, not affiliated). Combines WMN data with Sherlock and Maigret, with live results and JSON/CSV export. |

### ⌨️ Command-line and scripts
| Tool | Type | Description |
|------|------|-------------|
| [Naminter](https://github.com/3xp0rt/Naminter) | ![Python](https://img.shields.io/badge/-Python-3776AB?logo=python&logoColor=white) | Built specifically for this dataset. Supports Cloudflare bypass, browser impersonation, concurrent checking, and extensive config options. |
| [Blackbird](https://github.com/antoniaci/blackbird) | ![Python](https://img.shields.io/badge/-Python-3776AB?logo=python&logoColor=white) | Fast username search that integrates WMN data. |
| [WhatsMyName-Python](https://github.com/C3n7ral051nt4g3ncy/WhatsMyName-Python) | ![Python](https://img.shields.io/badge/-Python-3776AB?logo=python&logoColor=white) | Simple Python script by [@C3n7ral051nt4g3ncy](https://github.com/C3n7ral051nt4g3ncy). |

### 🖥️ Desktop, browser, and platforms
| Tool | Type | Description |
|------|------|-------------|
| [NameSeeker](https://github.com/funnyzak/name-seeker) | ![Tauri](https://img.shields.io/badge/-Tauri-FFC131?logo=tauri&logoColor=white) | Cross-platform desktop app for username and email search across hundreds of sites. Exports to PDF, CSV, and JSON. |
| [Maltego WhatsMyName Transforms](https://github.com/TURROKS/Maltego_WhatsMyName) | ![Maltego](https://img.shields.io/badge/-Maltego-1A1A1A) | Local Maltego transforms that check usernames in real time using the JSON file. |
| [Who Am I](https://chromewebstore.google.com/detail/who-am-i/gdnhlhadhgnhaenfcphpeakdghkccfoo) | ![Chrome Extension](https://img.shields.io/badge/-Chrome%20Extension-4285F4?logo=googlechrome&logoColor=white) | Chrome/Brave extension combining WMN data with Sherlock and Maigret, by [OSINT Liar](https://osintliar.com/). |
| [FreeUsername (Android)](https://play.google.com/store/apps/details?id=whatsmyname.app.us) | ![Android](https://img.shields.io/badge/-Android-3DDC84?logo=android&logoColor=white) | Android version of [FreeUsername](https://freeusername.com/), combining WMN data with Sherlock and Maigret. Checks run on the device. Exports to JSON and CSV. |

### 🐳 Self-hosted and containerized
| Tool | Type | Description |
|------|------|-------------|
| [WhatsMyName-Web](https://github.com/AXRoux/WhatsMyName-Web) | ![Flask](https://img.shields.io/badge/-Flask-000000?logo=flask&logoColor=white) | Simple Flask web app version of WhatsMyName by [@AXRoux](https://github.com/AXRoux/). |
| [WhatsMyName Docker](https://github.com/kodamaChameleon/wmn-docker) | ![Docker](https://img.shields.io/badge/-Docker-2496ED?logo=docker&logoColor=white) | Docker API wrapper over the WMN tool by [@kodamaChameleon](https://github.com/kodamaChameleon). |

---

## License

[![Creative Commons License](https://i.creativecommons.org/l/by-sa/4.0/88x31.png)](http://creativecommons.org/licenses/by-sa/4.0/)

This work is licensed under a [Creative Commons Attribution-ShareAlike 4.0 International License](http://creativecommons.org/licenses/by-sa/4.0/).
