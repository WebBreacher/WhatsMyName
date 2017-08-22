# WhatsMyName
This repository has the unified data required to perform user and username enumeration on various websites. 

Content is in a JSON file and can easily be used in other projects such as the ones below:
* [Recon-ng](https://bitbucket.org/LaNMaSteR53/recon-ng) - The [Profiler Module](https://bitbucket.org/LaNMaSteR53/recon-ng/src/7723096ce2301092906838ef73564e7907886748/modules/recon/profiles-profiles/profiler.py?at=master&fileviewer=file-view-default) grabs this JSON file and uses it. See https://webbreacher.com/2014/12/11/recon-ng-profiler-module/ for details. 
* [Spiderfoot](https://github.com/smicallef/spiderfoot) uses this in the [sfp_account](https://github.com/smicallef/spiderfoot/blob/master/modules/sfp_accounts.py) module. 

## Installation

The code can be installed by cloning the repository and installing via pip

```
pip install -e WhatsMyName
```


## Format
The format of the JSON is simple. There are 3 main elements:

1. License - The license for this project and its data
2. Authors - The people that have contributed to this project
3. Sites - This is the main data

Within the "sites" elements, the format is as follows (with several parameters being optional):

```json
     ...
      {
         "name" : "name of the site",
         "check_uri" : "URI to check the site with the {account} string replaced by a username",
         "pretty_uri" : "if the check_uri is for an API, this OPTIONAL element can show a human-readable page",
         "account_existence_code" : "the HTTP response code for a good 'account is there' response",
         "account_existence_string" : "the string in the response that we look for for a good response",
         "account_missing_string" : "this OPTIONAL string will only be in the response if there is no account found ",
         "account_missing_code" : "the HTTP response code for a bad 'account is not there' response",
         "known_accounts" : ["a list of user accounts that can be used to test","for user enumeration"],
         "allowed_types" : ["these are the types of data and categories of the content"],
         "category" : "a category for what the site is mainly used for",
         "valid" : "this true or false boolean field is used to enable or disable this site element",
         "comments" : ["a list of comments including when this was last verified and outcomes"]
      },
      ...
```

Here is an example of a site element:

```json
     ...
      {
         "name" : "GitHub",
         "check_uri" : "https://api.github.com/users/{account}",
         "pretty_uri" : "https://github.com/{account}",
         "account_existence_code" : "200",
         "account_existence_string" : "login:",
         "account_missing_string" : ["Not Found"],
         "account_missing_code" : "404",
         "known_accounts" : ["test","webbreacher"],
         "allowed_types" : ["String","Person","WebAccount","Username","Organization"],
         "category" : "coding",
         "valid" : true,
         "comments" : ["verified 11/08/2015 - webbreacher"]
      },
      ...
```

## Standalone Checker
If you just want to run this script to check user names on sites and don't wish to use it in combination with another tool (like Recon-NG and/or Spiderfoot), then you can use the included Python script as shown below:

```
 $  python -m whats_my_name -u username
Running
 -  174 sites found in file.
 -  Looking up https://about.me/username
[+] Found user at https://about.me/username
 *  Skipping AdultFriendFinder - Marked as not valid.
 -  Looking up https://angel.co/username?utm_source=people
      !  ERROR: BAD CODE AND STRING. Neither the HTTP response code or detection string worked.
 -  Looking up http://www.anobii.com/username/books
      !  ERROR: BAD DETECTION STRING. "- aNobii</title>" was not found on resulting page.
 -  Looking up http://ask.fm/username
[+] Found user at http://ask.fm/username
 -  Looking up https://username.atlassian.net/login
      !  ERROR: BAD DETECTION STRING. "Unable to access your account" was not found on resulting page.
 -  Looking up https://username.atlassian.net/admin/users/sign-up
      !  ERROR: BAD CODE AND STRING. Neither the HTTP response code or detection string worked.
 -  Looking up https://audioboom.com/username
^C !!!  You pressed Ctrl+C. Exiting script.
------------
The following previously "valid" sites had errors:
     AngelList --> Bad detection code and string. Received Code: 404; Expected Code: 200.
     Atlassian --> Bad detection string.
     Atlassian Self-Signup --> Bad detection code and string. Received Code: 502; Expected Code: 200.
     aNobil --> Bad detection string.
```

## Updates
I update this project as I have time and would *LOVE* to have interested people help maintain and grow it. 
Please reach to me webbreacher {at} gmail {dot} com if you are interested.

## Contributors
[@WebBreacher](https://github.com/WebBreacher/)<br>
[@Munchko](https://github.com/Munchko/)<br>
[@L0r3m1p5um](https://github.com/L0r3m1p5um/)<br>
[@lehuff](https://github.com/lehuff/)<br>
[@rpiguy](https://github.com/andydennis/)<br>
