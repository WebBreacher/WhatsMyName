![WhatsMyName](whatsmyname.png)

# WhatsMyName

[![License: CC BY-SA 4.0](https://img.shields.io/badge/license-CC--BY--SA--4.0-lightgrey)](http://creativecommons.org/licenses/by-sa/4.0/)
[![Sites tracked](https://img.shields.io/badge/dynamic/json?url=https%3A%2F%2Fraw.githubusercontent.com%2FWebBreacher%2FWhatsMyName%2Fmain%2Fwmn-data.json&query=%24.sites.length&label=sites&color=blue)](wmn-data.json)
[![Categories](https://img.shields.io/badge/dynamic/json?url=https%3A%2F%2Fraw.githubusercontent.com%2FWebBreacher%2FWhatsMyName%2Fmain%2Fwmn-data.json&query=%24.categories.length&label=categories&color=blue)](wmn-data.json)
[![Contributors](https://img.shields.io/github/contributors/WebBreacher/WhatsMyName)](https://github.com/WebBreacher/WhatsMyName/graphs/contributors)
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen)](CONTRIBUTING.md)
[![GitHub Stars](https://img.shields.io/github/stars/WebBreacher/WhatsMyName?style=social)](https://github.com/WebBreacher/WhatsMyName/stargazers)

**WhatsMyName (WMN) is a community-maintained dataset that lets you find out if a username exists across hundreds of websites.** If you're investigating a person of interest, verifying an online identity, or simply curious about your own digital footprint, this project powers the tools that make that possible.

Created in 2015 by [Micah "WebBreacher" Hoffman](https://webbreacher.com), WhatsMyName started as a personal fix for a real frustration: existing username checkers were full of false positives. Over the years, contributions from people all over the world have grown it into one of the most widely-used username enumeration datasets in the OSINT community.

## Table of Contents

- [Just want to search a username right now?](#just-want-to-search-a-username-right-now)
- [How It Works](#how-it-works)
- [Tools and Sites That Use WhatsMyName](#tools-and-sites-that-use-whatsmyname)
- [Help Keep WMN Accurate](#help-keep-wmn-accurate)
- [Stay Connected](#stay-connected)
- [License](#license)

---

## Just want to search a username right now?

Head to **[whatsmyname.app](https://whatsmyname.app/)** -- a free, browser-based tool built directly on this dataset. No installation required.

Or check out the [many tools below that use WMN](#tools-and-sites-that-use-whatsmyname).

---

## How It Works

WMN is a single, carefully maintained JSON file (`wmn-data.json`). Each entry describes how to check one website for a username -- what URL to query, what a successful response looks like, and what a "not found" response looks like.

Tools and scripts read this file and do the actual checking. That separation means anyone can build a checker, and the data stays accurate regardless of which tool you prefer.

**For a site to be included, it must:**

1. **Be publicly accessible** -- sites behind paywalls or login walls can't be checked
2. **Include the username in the URL** -- the profile URL must contain the username directly
3. **Not transform the username** -- sites that swap usernames for numeric IDs won't work

> In May 2023, we removed the bundled checker scripts and shifted focus entirely to maintaining the data file. See the tools section below for checkers that use our data.

---

## Tools and Sites That Use WhatsMyName

### Web-based (no install required)
| Tool | Description |
|------|-------------|
| [whatsmyname.app](https://whatsmyname.app/) | The go-to web interface by [Chris Poulter](https://twitter.com/osintcombine). Filters by category, exports to CSV, always pulls the latest data. |
| [Who Am I](https://chromewebstore.google.com/detail/who-am-i/gdnhlhadhgnhaenfcphpeakdghkccfoo) | Chrome/Brave extension combining WMN data with Sherlock and Maigret, by [OSINT Liar](https://osintliar.com/). |
| [K2OSINT Bookmarklet](https://github.com/K2SOsint/Bookmarklets/blob/main/WhatsMyName.js) | Browser bookmarklet -- enter a username in a popup, results open in a new tab. |

### Command-line and scripts
| Tool | Description |
|------|-------------|
| [Naminter](https://github.com/3xp0rt/Naminter) | Built specifically for this dataset. Supports Cloudflare bypass, browser impersonation, concurrent checking, and extensive config options. |
| [Blackbird](https://github.com/p1ngul1n0/blackbird) | Fast username search that integrates WMN data. |
| [WhatsMyName-Python](https://github.com/C3n7ral051nt4g3ncy/WhatsMyName-Python) | Simple Python script by [@C3n7ral051nt4g3ncy](https://github.com/C3n7ral051nt4g3ncy). |
| [WhatsMyName-Client](https://github.com/grabowskiadrian/WhatsMyName-Client) | Python script with request header and POST support by [@grabowskiadrian](https://github.com/grabowskiadrian). Also useful for testing the JSON config. |
| [Reveal My Name](https://github.com/yooper/reveal-my-name) | The original Python checker that shipped with this project, maintained by [@yooper](https://github.com/yooper). |
| [WMN Screenshooter](https://github.com/swedishmike/WMN_screenshooter) | Selenium-based helper that screenshots identified profile pages. |
| [sn0int](https://github.com/kpcyrd/sn0int) | Uses WMN data in the [kpcyrd/whatsmyname](https://sn0int.com/r/kpcyrd/whatsmyname) module. |

### Desktop and platforms
| Tool | Description |
|------|-------------|
| [NameSeeker](https://github.com/funnyzak/name-seeker) | Cross-platform desktop app for username and email search across hundreds of sites. Exports to PDF, CSV, and JSON. |
| [LinkScope](https://github.com/AccentuSoft/LinkScope_Client) | Uses WMN in its **Online Identity** category. |
| [Maltego WhatsMyName Transforms](https://github.com/TURROKS/Maltego_WhatsMyName) | Local Maltego transforms that check usernames in real time using the JSON file. |
| [Spiderfoot](https://github.com/smicallef/spiderfoot) | Integrates WMN in the `sfp_account` module. ([CLI demo video](https://asciinema.org/a/295923)) |

### Self-hosted and containerized
| Tool | Description |
|------|-------------|
| [WhatsMyName-Web](https://github.com/AXRoux/WhatsMyName-Web) | Simple Flask web app version of WhatsMyName by [@AXRoux](https://github.com/AXRoux/). |
| [WhatsMyName Docker](https://github.com/kodamaChameleon/wmn-docker) | Docker API wrapper over the WMN tool by [@kodamaChameleon](https://github.com/kodamaChameleon). |

---

## Help Keep WMN Accurate

This project only stays useful if the detections stay accurate. Websites change their profile URLs, response codes, and page content constantly. **We need contributors to help find new sites and fix broken detections.**

You don't need to be a developer. Here's how to help at any level:

| Experience level | How to contribute |
|-----------------|-------------------|
| No technical background | [Submit a site via this form](https://forms.office.com/r/TscnNQqrD1) |
| Comfortable with GitHub | [Open an issue](https://github.com/WebBreacher/WhatsMyName/issues) with a link to an example profile |
| Comfortable with JSON and HTTP | Fork the repo, fix or add a detection, and submit a pull request |

See [CONTRIBUTING.md](CONTRIBUTING.md) for detailed instructions on adding or fixing site detections, including format requirements and examples.

---

## Stay Connected

Follow the project on [BlueSky](https://bsky.app/profile/whatsmyna.me) for updates.

---

## License

[![Creative Commons License](https://i.creativecommons.org/l/by-sa/4.0/88x31.png)](http://creativecommons.org/licenses/by-sa/4.0/)

This work is licensed under a [Creative Commons Attribution-ShareAlike 4.0 International License](http://creativecommons.org/licenses/by-sa/4.0/).
