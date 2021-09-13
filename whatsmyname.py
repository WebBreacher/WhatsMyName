#!/usr/bin/python

'''

This script does several things:
1. It checks all the detection strings to ensure they are accurate
2. It can be used to check for a username across 1 or more sites

'''

import argparse
import collections
import json
import os
import random
import signal
import string
import sys

from selenium import webdriver as wd
from seleniumwire import webdriver as wdwire
from selenium.webdriver.firefox.options import Options

COUNTER = collections.Counter()

# Selenium Options
opts = Options()
opts.headless = True

debug_mode = False
user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko)  Chrome/93.0.4577.63 Safari/537.36'

# Set HTTP Header info.
HEADERS = {'Accept' : 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
           'Accept-Language' : 'en-US,en;q=0.5',
           'Accept-Encoding' : 'gzip, deflate'
          }

# Command line input
parser = argparse.ArgumentParser(description='This standalone script will look up a single username using the JSON file'
                                 ' or, if no usernames are passed to it, will run a check of the JSON file for bad'
                                 ' detection strings.')
parser.add_argument('-a', '--useragent', help="Toggle using a custom UserAgent for web calls [Default = off]", action="store_true",
                    default=False)
parser.add_argument('-d', '--debug', help="Enable debug output [Default = off]", action="store_true")
parser.add_argument('-in', '--inputfile', nargs='?', help="[OPTIONAL] Uses a specified file for checking the websites")
parser.add_argument('-s', '--site', nargs='*', help='If this parameter is passed the script will check only the named site'
                    ' or list of sites.')
parser.add_argument('-u', '--username', help='If this param is passed then this script will perform the '
                    'lookups against the given user name instead of running checks against the JSON file.')

if os.name == "posix":
    class Colors:
        YELLOW = "\033[93m"
        RED = "\033[91m"
        GREEN = "\033[92m"
        ENDC = "\033[0m"
else:
    class Colors:
        YELLOW = ""
        RED = ""
        GREEN = ""
        ENDC = ""

def warn(msg):
    print(Colors.YELLOW + msg + Colors.ENDC)
def error(msg):
    print(Colors.RED + msg + Colors.ENDC)
def positive(msg):
    print(Colors.GREEN + msg + Colors.ENDC)
def neutral(msg):
    print(msg)

def signal_handler(*_):
    error(' !!!  You pressed Ctrl+C. Exiting script.')
    sys.exit(130)

def web_call_response_code(location):
    # Get HTTP Response Code using Selenium-wire
    if debug_mode:
        print('- Requesting site for HTTP response code.')
    driver_wire = wdwire.Firefox(options=opts)
    driver_wire.get(location)
    for request in driver_wire.requests:
        if location in request.url:
            if request.response:
                if debug_mode:
                    print(request.url,request.response.status_code)
                code = request.response.status_code
    driver_wire.close()
    return code

def web_call_html_source(location):
    # Get HTML source using Selenium for JS bypassing
    if debug_mode:
        print('- Requesting site for HTML.')
    driver = wd.Firefox(options=opts)
    driver.get(location)
    source = driver.page_source
    driver.close()
    return source

def find_sites_to_check(args, data):
    if args.site:
        # cut the list of sites down to only the requested one
        args.site = [x.lower() for x in args.site]
        sites_to_check = [x for x in data['sites'] if x['name'].lower() in args.site]
        if sites_to_check == 0:
            error('Sorry, none of the requested site or sites were found in the list')
            sys.exit(1)
        sites_not_found = len(args.site) - len(sites_to_check)
        if sites_not_found:
            warn('WARNING: %d requested sites were not found in the list' % sites_not_found)
        neutral(' Checking %d sites' % len(sites_to_check))
        return sites_to_check
    else:
        neutral('%d sites found in file.' % len(data['sites']))
        return data['sites']

def check_site(site, username, if_found, if_not_found, if_neither):
    url = site['check_uri'].replace("{account}", username)
    try:
        resp_code = web_call_response_code(url)
        code_match = resp_code == int(site['account_existence_code'])

        resp_html_source = web_call_html_source(url)
        string_match = resp_html_source.find(site['account_existence_string']) > 0

        if debug_mode:
            neutral("- HTTP status (match %s): %s " % (code_match, resp_code))
            neutral("- HTTP response (match: %s): %s" % (string_match, resp_html_source))

        if code_match and string_match:
            COUNTER["FOUND"] += 1
            return if_found(url)

        code_missing_match = resp_code == int(site['account_missing_code'])
        string_missing_match = resp_html_source.find(site['account_missing_string']) > 0

        if code_missing_match or string_missing_match:
            COUNTER["NOT_FOUND"] += 1
            return if_not_found(url)

        COUNTER["ERROR"] += 1
        return if_neither(url)

    except Exception as caught:
        COUNTER["ERROR"] += 1
        error("Error when looking up %s (%s)" % (url, str(caught)))

###################
# Main
###################

def main():
    args = parser.parse_args()

    if args.debug:
        global debug_mode
        debug_mode = args.debug
        print('Debug output enabled')

    if args.useragent:
        HEADERS['User-Agent'] = user_agent
        print('Custom UserAgent enabled')

    # Add this in case user presses CTRL-C
    signal.signal(signal.SIGINT, signal_handler)

    # Read in the JSON file
    if (args.inputfile):
        inputfile = args.inputfile
    else:
        inputfile = 'web_accounts_list.json'

    with open(inputfile) as data_file:
        data = json.load(data_file)

    sites_to_check = find_sites_to_check(args, data)

    try:
        for site in sites_to_check:
            if not site['valid']:
                warn("[!] Skipping %s - Marked as not valid." % site['name'])
                continue

            if args.username:
                check_site(site, args.username,
                           if_found     = lambda url: positive("[+] User found at %s" % url),
                           if_not_found = lambda url: neutral( "[-] User not found at %s" % url),
                           if_neither   = lambda url: error(   "[! ] Error. The check implementation is broken for %s" % url))
            else:
                non_existent = ''.join(random.choice(string.ascii_lowercase + string.ascii_uppercase + string.digits) for x in range(10))

                check_site(site, non_existent,
                           if_found     = lambda url: error(  "[!] False positive for %s" % url),
                           if_not_found = lambda url: neutral("    As expected, no user found at %s" % url),
                           if_neither   = lambda url: error(  "[!] Neither conditions matched for %s" % url))

                for known_account in site['known_accounts']:
                    check_site(site, known_account,
                               if_found     = lambda url: neutral("    As expected, profile found at %s" % url),
                               if_not_found = lambda url: error(  "[!] Profile not found at %s" % url),
                               if_neither   = lambda url: error(  "[!] Neither conditions matched for %s" % url))
    finally:
        neutral("")
        neutral("Processing completed")
        if COUNTER["FOUND"]:
           positive("%d sites found" % COUNTER["FOUND"])
        if COUNTER["ERROR"]:
           error("%d errors encountered" % COUNTER["ERROR"])
           sys.exit(2)

if __name__ == "__main__":
    # execute only if run as a script
    main()
