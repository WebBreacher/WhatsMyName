# WhatsMyName

This repository has the data required to perform username enumeration on various websites. Content is in a JSON file and can easily be used in other projects such as the ones below:

<img src="https://github.com/WebBreacher/WhatsMyName/blob/main/whatsmyname.png" width="200">

## Tools/Web Sites Using WhatsMyName

* https://whatsmyname.app/ - [Chris Poulter](https://twitter.com/osintcombine) created this site which draws the project's JSON file into an easy to use web interface.
  * Filters for category and in search results.
  * Exports to CSV and other formats.
  * Pulls the latest version of the project's JSON file when run.
  * Submit a username in the URL using `https://whatsmyname.app/?q=USERNAME` like https://whatsmyname.app/?q=john
* [Reveal My Name](https://github.com/yooper/reveal-my-name) is created by [@yooper](https://github.com/yooper) and is the Python checker tool that was bundled with this project.
* [Spiderfoot](https://github.com/smicallef/spiderfoot) uses this in the **sfp_account** module. There is also [this video](https://asciinema.org/a/295923) showing how to use this project using the Spiderfoot Command Line Interface (CLI).
* [sn0int](https://github.com/kpcyrd/sn0int) downloads and uses the JSON file in the [kpcyrd/whatsmyname](https://sn0int.com/r/kpcyrd/whatsmyname) module, see https://twitter.com/sn0int/status/1228046880459907073 for details and instructions.
* [WMN_screenshooter](https://github.com/swedishmike/WMN_screenshooter) a helper script that is based on `web_accounts_list_checker.py` and uses Selenium to try and grab screenshots of identified profile pages.
* [LinkScope](https://github.com/AccentuSoft/LinkScope_Client) uses this in the **Whats My Name** resolution under the **Online Identity** category.
* [Blackbird](https://github.com/p1ngul1n0/blackbird) uses the **Whats My Name** list in its search.
* [WhatsMyName-Python](https://github.com/C3n7ral051nt4g3ncy/WhatsMyName-Python) **Whats My Name** simple Python script made by [@C3n7ral051nt4g3ncy](https://github.com/C3n7ral051nt4g3ncy)
* [K2OSINT Bookmarklet](https://github.com/K2SOsint/Bookmarklets/blob/main/WhatsMyName.js) - Bookmarklet that lets you enter a username in a popup and then opens a new tab with the WMN results.


## Content

* The https://github.com/WebBreacher/WhatsMyName/wiki/Problem-Removed-Sites page has websites that we have had in the project and are currently not working for some reason. We will retest those sites (in the future) and try to find detections.
* If you would like to help with detections, we are happy to accept them via GitHub pull request or you can [create an issue](https://github.com/WebBreacher/WhatsMyName/issues) with the details of the site.
* Want to suggest a site to be added? Use [this form](https://spotinfo.co/535y).


## Format

See [CONTRIBUTING](CONTRIBUTING.md)


# Social Media
Come follow us for updates. We are on:
* Mastodon at https://infosec.exchange/@whatsmyname <a rel="me" href="https://infosec.exchange/@whatsmyname"></a>
* Twitter at https://twitter.com/whatsmynameproj


# Installation (Not applicable anymore)
Since our decision to remove all checker scripts from the project in May 2023 so we can focus on the detection JSON file, you will need to use WhatsMyName through a third party tool like those linked on https://github.com/WebBreacher/WhatsMyName/blob/main/README.md#toolsweb-sites-using-whatsmyname


# License
<a rel="license" href="http://creativecommons.org/licenses/by-sa/4.0/"><img alt="Creative Commons License" style="border-width:0" src="https://i.creativecommons.org/l/by-sa/4.0/88x31.png" /></a><br />This work is licensed under a <a rel="license" href="http://creativecommons.org/licenses/by-sa/4.0/">Creative Commons Attribution-ShareAlike 4.0 International License</a>.
