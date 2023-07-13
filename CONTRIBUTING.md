You can contribute to the project in at least a couple ways.

## Method 1. Non-technical

Suggest a new site to be covered by the tool.

How to do that:

- Find the new site which has public profiles of people (with no authentication required)
- Use [this form](https://spotinfo.co/535y) to tell us about it.... OR....
- Create a Github Issue and submit the link to an example profile. You can
  do that by navigating to [Issues](https://github.com/WebBreacher/WhatsMyName/issues)
  and clicking "New issue"


## Method 2. Technical, no programming skills required

Requires a basic understanding of how Web/HTTP works (HTTP status codes, how
what you see in a website translates to the source code).
And some experience in Github contributions (fork, pull-request).

Implement support for a new site or fix an existing implementation for a site.

How to do that:

- Among existing [Issues](https://github.com/WebBreacher/WhatsMyName/issues)
  or from somewhere else, establish which site you want to add
- Using a web client of your choice (preferred `curl` or `wget`) perform
  simple requests for two different scenarios: existing profile,
  non-existing profile, e.g.
  ```
  # existing
  curl https://twitter.com/WebBreacher

  # non-existing
  curl https://twitter.com/ThisDoesNotExistForSure504
  ```
- Observe the outcome for non-existing profile. Some sites use 404 (error), some use 302
(redirection), some confusingly use 200 (OK) for profiles which don't exist,
e.g.
  ```
  $ curl https://github.com/ThisDoesNotExistForSure504
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
- Add a section to `wmn-data.json`
- Test your configuration by running the tool for a given site
- Submit a pull request with that change
- There is also the `sample.json` file that you can use for testing. Simply replace the existing content with new data and test.

## Format of the JSON File

### Format of the New/Current JSON file

The format of the `wmn-data.json` JSON was altered due to Issue #414. There are still 3 main elements:

1. License - The license for this project and its data
2. Authors - The people that have contributed to this project
3. Sites - This is the main data

Within the `sites` elements, the format is as follows (with several parameters being optional):

```json
     ...
      {
         "name" : "name of the site",
         "uri_check" : "URI to check the site with the {account} string replaced by a username",
         "uri_pretty" : "if the check_uri is for an API, this OPTIONAL element can show a human-readable page",
         "post_body" : "[OPTIONAL] if non-empty, then this entry is an HTTP POST and the content of this field are the data",
         "invalid_chars" : "[OPTIONAL] if non-empty then checking apps should ignore or strip these characters from usernames",
         "e_code" : "the HTTP response code for a good 'account is there' response as an integer",
         "e_string" : "the string in the response that we look for for a good response",
         "m_string" : "this OPTIONAL string will only be in the response if there is no account found ",
         "m_code" : "the HTTP response code for a bad 'account is not there' response as an integer",
         "known" : ["a list of user accounts that can be used to test", "for user enumeration"],
         "cat" : "a category for what the site is mainly used for. These are found at the top of the JSON",
         "valid" : "this true or false boolean field is used to enable or disable this site element"
      },
      ...
```

Here are examples of the site elements for both HTTP GET and HTTP POST entries:

**HTTP GET entry:**

```json
     {
       "name" : "Example GET",
       "uri_check" : "https://www.example.com/load_profile_info.php?name={account}",
       "uri_pretty" : "https://www.test.com/profile/{account}",
       "e_code" : 200,
       "e_string" : "regist_at",
       "m_code" : 404,
       "m_string" : "Account not found",
       "known" : ["whoami", "johndoe"],
       "cat" : "images",
       "valid" : true
     },
```

**HTTP POST entry:**

```json
     {
       "name" : "Example POST",
       "uri_check" : "https://www.example.com/interact_api/load_profile_info.php",
       "post_body" : "Name=Gareth+Wylie&Age=24&Formula=a%2Bb+%3D%3D+21",
       "e_code" : 200,
       "e_string" : "regist_at",
       "m_code" : 404,
       "m_string" : "Account not found",
       "known" : ["whoami", "johndoe"],
       "cat" : "images",
       "valid" : true
     },
```
