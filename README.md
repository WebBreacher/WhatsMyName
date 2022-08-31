# WhatsMyName

This repository has the unified data required to perform user and username enumeration on various websites. Content is in a JSON file and can easily be used in other projects such as the ones below:

![whatsmyname](whatsmyname.png)

## Tools/Web Sites Using WhatsMyName

* https://whatsmyname.app/ - [Chris Poulter](https://twitter.com/osintcombine) created this site which draws the project's JSON file into a gorgeous and easy to use web interface.
  * Filters for category and in search results.
  * Exports to CSV and other formats.
  * Pulls the latest version of the project's JSON file when run.
  * Submit a username in the URL using `https://whatsmyname.app/?q=USERNAME` like https://whatsmyname.app/?q=john
* [Spiderfoot](https://github.com/smicallef/spiderfoot) uses this in the **sfp_account** module. There is also [this video](https://asciinema.org/a/295923) showing how to use this project using the Spiderfoot Command Line Interface (CLI).
* [Recon-ng](https://github.com/lanmaster53/recon-ng) - The **Profiler Module** uses this project's JSON content.
* [sn0int](https://github.com/kpcyrd/sn0int) downloads and uses the JSON file in the [kpcyrd/whatsmyname](https://sn0int.com/r/kpcyrd/whatsmyname) module, see https://twitter.com/sn0int/status/1228046880459907073 for details and instructions.
* [WMN_screenshooter](https://github.com/swedishmike/WMN_screenshooter) a helper script that is based on `web_accounts_list_checker.py` and uses Selenium to try and grab screenshots of identified profile pages.
* [LinkScope](https://github.com/AccentuSoft/LinkScope_Client) uses this in the **Whats My Name** resolution under the **Online Identity** category.
* [Blackbird](https://github.com/p1ngul1n0/blackbird) uses the **Whats My Name** list in its search.


## Content

* The https://github.com/WebBreacher/WhatsMyName/wiki/Problem-Removed-Sites page has websites that we have had in the project and are currently not working for some reason. We will retest those sites (in the future) and try to find detections.
* If you would like to help with detections, we are happy to accept them via GitHub Pull Request or you can [create an issue](https://github.com/WebBreacher/WhatsMyName/issues) with the details of the site.
* Want to suggest a site to be added? Use [this form](https://spotinfo.co/535y).

# Format

See [CONTRIBUTING](CONTRIBUTING.md)

# Standalone Checkers
If you just want to run this script to check user names on sites and don't wish to use it in combination with another tool (like https://whatsmyname.app and/or Spiderfoot), then you can use the included Python 3 scripts as shown below. There is the `web_accounts_list_checker.py` (preferred) and the `check_online_presence.py` which will take MUCH longer to cycle through all the sites and it works a bit differently than the first one.

```
 $  python3 ./web_accounts_list_checker.py -u maxim
 -  424 sites found in file.
 >  Looking up https://www.7cups.com/@maxim
 >  Looking up https://artistsnclients.com/people/maxim
 >  Looking up https://ameblo.jp/maxim
 >  Looking up https://aminoapps.com/u/maxim
 >  Looking up https://www.anime-planet.com/users/maxim
 >  Looking up https://apex.tracker.gg/apex/profile/origin/maxim/overview
 >  Looking up https://asciinema.org/~maxim
 >  Looking up https://audiojungle.net/user/maxim
 >  Looking up https://community.avid.com/members/maxim/default.aspx
 *  Skipping BiggerPockets - Marked as not valid.
...
[SNIPPED for brevity]
...
-------------------------------------------
Searching for sites with username (maxim) > Found 159 results:

[+] Found user at https://coderwall.com/maxim/
[+] Found user at https://dev.to/maxim
[+] Found user at https://www.designspiration.com/maxim/
[+] Found user at https://community.cloudflare.com/u/maxim
[+] Found user at https://maxim.carrd.co
[+] Found user at https://maxim.gumroad.com/
...
```

# Contributors
We would like to thank our contributors for their work. Whether it was adding sites, making our logo, fixing some broken code, or enhancing the project in many other ways! We appreciate the time you volunteered!

[@WebBreacher](https://github.com/WebBreacher/), [@Munchko](https://github.com/Munchko/), [@L0r3m1p5um](https://github.com/L0r3m1p5um/), [@lehuff](https://github.com/lehuff/), [@arnydo](https://github.com/arnydo), [@janbinx](https://github.com/janbinx/), [@bcoles](https://github.com/bcoles), [@Sector035](https://github.com/sector035/), [@mccartney](https://github.com/mccartney), [@salaheldinaz](https://github.com/salaheldinaz), [@camhoff](https://github.com/spotlightc), [@BerndDasByte](https://github.com/BerndDasByte/), [@jocephus](https://github.com/jocephus/), [@swedishmike](https://github.com/swedishmike/), [@soxoj](https://github.com/soxoj/), [@jspinel](https://github.com/jspinel), [@ef1500](https://github.com/ef1500), [@iamzewen](https://github.com/iamzewen), [@jocejocejoe](https://github.com/jocejocejoe), [@K2SOsint](https://github.com/k2sosint), [@C3n7ral051nt4g3ncy](https://github.com/C3n7ral051nt4g3ncy)

# License
<a rel="license" href="http://creativecommons.org/licenses/by-sa/4.0/"><img alt="Creative Commons License" style="border-width:0" src="https://i.creativecommons.org/l/by-sa/4.0/88x31.png" /></a><br />This work is licensed under a <a rel="license" href="http://creativecommons.org/licenses/by-sa/4.0/">Creative Commons Attribution-ShareAlike 4.0 International License</a>.
