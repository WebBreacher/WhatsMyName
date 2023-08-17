<p align="center">
  <img src="https://github.com/WebBreacher/WhatsMyName/blob/main/whatsmyname.png" width="400">
</p>

# WhatsMyName

What is WhatsMyName? It is a project that [Micah "WebBreacher" Hoffman](https://webbreacher.com) created in 2015 with the goal of discovering if usernames were used on a given website. He was frustrated with the false positives that were present in the username checkers of that time and so he made his own. Fast forward to today and many people have helped this open-source project evolve into what it is today.

If you are an OSINT person that has come here to run the tool, well, you are probably a bit disappointed right now. In May 2023, we decided to remove all checker scripts from the project and just focus on the project's core; its data file (`wmn-dat.json`).

So, we will keep finding sites and adding them and you can feel free to try any of the checker sites and scripts below that use our data.


## How Does It Work?

WhatsMyName (WMN) consists of a JSON file with detections in it. Submissions from people all over the world are included. When a request is made to one of those sites from a tool like the ones in the next section, the server replies with data that will match one of our detections. It'll tell the checker script whether there a valid user account with the name we specified on their site or not.

For a site to be included in WMN it has to:

1. **Be accessible.** _We cannot check sites behind paywalls or user authentication._
2. **Put the username in the URL.** _If the URL to view a user's profile does not have that username in it, this tool won't work._
3. **Not modify the username in the URL.** _URLs that have added user ID numbers to the username will not work in WMN. Also, sites that take your username and map it to a user ID number and then put that in the URL will not work._


## Tools/Web Sites Using WhatsMyName

* https://whatsmyname.app/ - [Chris Poulter](https://twitter.com/osintcombine) created this site which draws the project's JSON file into an easy to use web interface.
  * Filters for category and in search results.
  * Exports to CSV and other formats.
  * Pulls the latest version of the project's JSON file when run.
  * Submit a username in the URL using `https://whatsmyname.app/?q=USERNAME` like https://whatsmyname.app/?q=john
* [Blackbird](https://github.com/p1ngul1n0/blackbird) uses the **Whats My Name** list in its search.
* [K2OSINT Bookmarklet](https://github.com/K2SOsint/Bookmarklets/blob/main/WhatsMyName.js) - Bookmarklet that lets you enter a username in a popup and then opens a new tab with the WMN results.
* [LinkScope](https://github.com/AccentuSoft/LinkScope_Client) uses this in the **Whats My Name** resolution under the **Online Identity** category.
* [Maltego WhatsMyName Transforms](https://github.com/TURROKS/Maltego_WhatsMyName) - **Maltego Local Transforms** that leverage the JSON file and check for usernames in real time.
* [Reveal My Name](https://github.com/yooper/reveal-my-name) is created by [@yooper](https://github.com/yooper) and is the Python checker tool that was bundled with this project.
* [sn0int](https://github.com/kpcyrd/sn0int) downloads and uses the JSON file in the [kpcyrd/whatsmyname](https://sn0int.com/r/kpcyrd/whatsmyname) module, see https://twitter.com/sn0int/status/1228046880459907073 for details and instructions.
* [Spiderfoot](https://github.com/smicallef/spiderfoot) uses this in the **sfp_account** module. There is also [this video](https://asciinema.org/a/295923) showing how to use this project using the Spiderfoot Command Line Interface (CLI).
* [WhatsMyName-Python](https://github.com/C3n7ral051nt4g3ncy/WhatsMyName-Python) **Whats My Name** simple Python script made by [@C3n7ral051nt4g3ncy](https://github.com/C3n7ral051nt4g3ncy)
* [WMN_screenshooter](https://github.com/swedishmike/WMN_screenshooter) a helper script that uses Selenium to try and grab screenshots of identified profile pages.


## Content

* The https://github.com/WebBreacher/WhatsMyName/wiki/Problem-Removed-Sites page has websites that we have had in the project and are currently not working for some reason. We will retest those sites (in the future) and try to find detections.
* If you would like to help with detections, we are happy to accept them via GitHub pull request or you can [create an issue](https://github.com/WebBreacher/WhatsMyName/issues) with the details of the site.
* Want to suggest a site to be added? Use [this form](https://spotinfo.co/535y).


## Format

See [CONTRIBUTING](CONTRIBUTING.md)


# Social Media

Come follow us for updates. We are on:
* Mastodon at https://infosec.exchange/@whatsmyname <a rel="me" href="https://infosec.exchange/@whatsmyname"></a>


# License

<a rel="license" href="http://creativecommons.org/licenses/by-sa/4.0/"><img alt="Creative Commons License" style="border-width:0" src="https://i.creativecommons.org/l/by-sa/4.0/88x31.png" /></a><br />This work is licensed under a <a rel="license" href="http://creativecommons.org/licenses/by-sa/4.0/">Creative Commons Attribution-ShareAlike 4.0 International License</a>.
