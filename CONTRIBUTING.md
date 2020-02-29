You can contribute to the project in at least three different ways.

## Way 1. Non-technical

Suggest a new site to be covered by the tool.

How to do that:

- Find the new site which has public profiles of people (with no authentication required)
- Create a Github Issue and submit the link to an example profile. You can
  do that by navigating to [Issues](https://github.com/ekalinin/github-markdown-toc/issues)
  and clicking "New issue"


## Way 2. Technical, no programming skills required

Requires a basic understanding of how Web/HTTP works (HTTP status codes, how
what you see in a website translates to the source code).
And some experience in Github contributions (fork, pull-request).

Implement support for a new site or fix an existing implementation for a site.

How to do that:

- Among existing [Issues](https://github.com/ekalinin/github-markdown-toc/issues)
  or from somewhere else, establish which site you want to add
- Using a web client of your choice (preferred `curl` or `wget`) perform
  simple requests for two different scenarios: existing profile,
  non-existing profile, e.g.
  ```
  # existing
  wget https://github.com/WebBreacher

  # non-existing
  wget https://github.com/ThisDoesNotExistForSure504
  ```
- Observe the outcome for non-existing profile. Some sites use 404 (error), some use 302
(redirection), some confusingly use 200 (OK) for profiles which don't exist,
e.g.
  ```
  $ wget https://github.com/ThisDoesNotExistForSure504
  [...]
  HTTP request sent, awaiting response... 404 Not Found 
  ```
- Observe the outcome for existing profile. The response code should be 200.
And among the downloaded source code find a text expected to be observed in
all profiles. Avoid picking a text which might be dynamic (e.g. include the
profile name).
This seems right:
```
<h2>You are browsing the profile of
```
This is too specific:
```
<h2>You are browsing the profile of WebBreacher</h2>
```
- add a section to `web_accounts_list.json`
- test your configuration by running the tool for a given site, e.g.
```
python3 ./web_accounts_list_checker.py -s my.new.site.Ive.added
```
- submit a pull request with that change


== Format of the JSON file

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
         "category" : "a category for what the site is mainly used for",
         "valid" : "this true or false boolean field is used to enable or disable this site element"
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
         "category" : "coding",
         "valid" : true
      },
      ...
```

## Way 3. Programming, enhancing the tool itself

Basic python programming skills required.

