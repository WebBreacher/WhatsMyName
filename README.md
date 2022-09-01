# WhatsMyName

This repository has the unified data required to perform user and username enumeration on various websites. Content is in a JSON file and can easily be used in other projects such as the ones below:

![whatsmyname](whatsmyname.png)

## Tools/Web Sites Using WhatsMyName

* https://whatsmyname.app/ - [Chris Poulter](https://twitter.com/osintcombine) created this site which draws the project's JSON file into an easy to use web interface.
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

## Format

See [CONTRIBUTING](CONTRIBUTING.md)

## Command Line Arguments
If you just want to run this script to check user names on sites and don't wish to use it in combination with another tool (like https://whatsmyname.app and/or Spiderfoot), then you can use the included Python 3 script, `what-is-my-name.py` as shown below.

There are quite a few command line options available

- Check for the users yooper and maxim, defaults to outputing json to stdout, only returns the found results.

`python whats_my_name.py -u yooper maxim`

- Check for the users yooper and maxim, defaults to outputing json to stdout, returns the not found and found results.

`python whats_my_name.py -u yooper maxim -a`

- Check for the users yooper and maxim, defaults to outputing json to stdout, returns the sites where no matches were found.

`python whats_my_name.py -u yooper maxim -n`

- Check for the user yooper, on social sites

`python whats_my_name.py -u yooper -c social`

- Check for the user yooper, on social sites, using a different web browser agent

`python whats_my_name.py -u yooper -c social --user_agent_platform 'Firefox on macOS' `

- Check for the user yooper, print out in a table format into console

`python whats_my_name.py -u yooper -c social --format table`

- Check for the user yooper, print out in a csv format into console

`python whats_my_name.py -u yooper -c social --format csv`

- Check for the user yooper, print out in a json (default) format into console

`python whats_my_name.py -u yooper -c social --format json`

- Check for the user yooper, capture errors for debugging purposes

`python whats_my_name.py -u yooper -c social --capture_errors`

# Contributors
We would like to thank our contributors for their work. Whether it was adding sites, making our logo, fixing some broken code, or enhancing the project in many other ways! We appreciate the time you volunteered!

[@WebBreacher](https://github.com/WebBreacher/), [@yooper](https://github.com/yooper/), [@Munchko](https://github.com/Munchko/), [@L0r3m1p5um](https://github.com/L0r3m1p5um/), [@lehuff](https://github.com/lehuff/), [@arnydo](https://github.com/arnydo), [@janbinx](https://github.com/janbinx/), [@bcoles](https://github.com/bcoles), [@Sector035](https://github.com/sector035/), [@mccartney](https://github.com/mccartney), [@salaheldinaz](https://github.com/salaheldinaz), [@camhoff](https://github.com/spotlightc), [@BerndDasByte](https://github.com/BerndDasByte/), [@jocephus](https://github.com/jocephus/), [@swedishmike](https://github.com/swedishmike/), [@soxoj](https://github.com/soxoj/), [@jspinel](https://github.com/jspinel), [@ef1500](https://github.com/ef1500), [@iamzewen](https://github.com/iamzewen), [@jocejocejoe](https://github.com/jocejocejoe), [@K2SOsint](https://github.com/k2sosint), [@C3n7ral051nt4g3ncy](https://github.com/C3n7ral051nt4g3ncy)

# License
<a rel="license" href="http://creativecommons.org/licenses/by-sa/4.0/"><img alt="Creative Commons License" style="border-width:0" src="https://i.creativecommons.org/l/by-sa/4.0/88x31.png" /></a><br />This work is licensed under a <a rel="license" href="http://creativecommons.org/licenses/by-sa/4.0/">Creative Commons Attribution-ShareAlike 4.0 International License</a>.
