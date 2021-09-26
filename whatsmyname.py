#!/usr/bin/python

'''

This script does several things:
1. It checks all the detection strings to ensure they are accurate
2. It can be used to check for a username across 1 or more sites

'''

# Todo:
# 1. CSV output
# 2. threading
# 7. Detect if username has non-url-friendly characters and would be used as subdomain
    # and not run tests on sites that don't make sense
# 8. Ctrl-C chould generate output of already-checked sites both to file and to screen
# 9. Switch to Chromedriver


#
# Import Libraries
#

import argparse
#import codecs
import collections
from datetime import datetime
import json
import os
import random
import signal
import string
import sys
import threading
import time

from selenium import webdriver as wd
from seleniumwire import webdriver as wdwire
#from selenium.webdriver.firefox.options import Options
from selenium.webdriver.chrome.options import Options

#
# Variables and Setup
#

COUNTER = collections.Counter()

debug_mode = False
running_positives = []
user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko)  Chrome/93.0.4577.63 Safari/537.36'
chromedriver_loc = '../../chromedriver-v94.exe' # Where is the chromedriver located?

# Set HTTP Header information
HEADERS = {'Accept' : 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
           'Accept-Language' : 'en-US,en;q=0.5',
           'Accept-Encoding' : 'gzip, deflate'
          }

# Command line input
parser = argparse.ArgumentParser(description='This standalone script will look up a single username using the JSON file'
                                 ' and output a text file with positive results. or, if no usernames are passed to it,'
                                 ' will run a check of the JSON file for bad detection strings.')
parser.add_argument('-a', '--useragent', help='Toggle using a custom UserAgent for web calls [Default = off]', action='store_true',
                    default=False)
parser.add_argument('-d', '--debug', help='Enable debug output [Default = off]', action='store_true')
parser.add_argument('-i', '--inputfile', nargs='?', help='[OPTIONAL] If you want to use a JSON file other than the main one,'
                    ' pass the file name here.')
parser.add_argument('-s', '--site', nargs='*', help='If this parameter is passed the script will check only the named site'
                    ' or list of sites.')
parser.add_argument('-u', '--username', help='If this param is passed then this script will perform the '
                    'lookups against the given user name instead of running checks against the JSON file.')

if os.name == 'posix':
    class Colors:
        RED = "\033[91m"
        GREEN = "\033[92m"
        YELLOW = "\033[93m"
        MAGENTA = "\033[95m"
        CYAN = "\033[96m"
        ENDC = "\033[0m"
else:
    class Colors:
        RED = ''
        GREEN = ''
        YELLOW = ''
        MAGENTA = ''
        CYAN = ''
        ENDC = ''

# Selenium Options for Firefox driver
#opts = Options()
#opts.headless = True

# Selenium Chrome Driver options
chrome_options = Options()
chrome_options.add_argument("--disable-extensions")
chrome_options.add_argument("--disable-gpu")
chrome_options.add_argument("--headless")
chrome_options.add_argument("--window-size=1920x1080")
chrome_options.add_experimental_option('excludeSwitches', ['enable-logging'])

#
# Functions
#

# Colorization
def error(msg):
    print(Colors.RED + '[!] ERROR! ' + msg + Colors.ENDC)

def positive(msg):
    print(Colors.GREEN + '[+] ' +msg + Colors.ENDC)

def warn(msg):
    print(Colors.YELLOW + '[*] WARNING. ' + msg + Colors.ENDC)

def startstop(msg):
    print(Colors.CYAN + msg + Colors.ENDC)

def debug(msg):
    print(Colors.MAGENTA + '[>] ' + msg + Colors.ENDC)

def negative(msg):
    print('[-] ' + msg)

def neutral(msg):
    print('[ ] ' + msg)

def signal_handler(*_):
    error('You pressed Ctrl+C. Exiting script.')
    sys.exit(130)

def web_call_response_code(location):
    # Get HTTP Response Code using Selenium-wire
    #driver_wire = wdwire.Firefox(options=opts)
    driver_wire = wdwire.Chrome(chromedriver_loc, options=chrome_options)
    driver_wire.set_page_load_timeout(30)
    driver_wire.get(location)
    for request in driver_wire.requests:
        if location in request.url:
            if request.response:
                if debug_mode:
                    debug(f'URL: {request.url}, HTTP Response Code: {request.response.status_code}')
                code = request.response.status_code
    driver_wire.close()
    return code

def web_call_html_source(location):
    # Get HTML source using Selenium for JS bypassing
    #driver = wd.Firefox(options=opts)
    driver = wd.Chrome(chromedriver_loc, options=chrome_options)
    driver.set_page_load_timeout(30)
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
            warn(f'{sites_not_found} requested sites were not found in the list')
        neutral('Checking %d sites' % len(sites_to_check))
        return sites_to_check
    else:
        startstop('')
        neutral(f'{len(data["sites"])} sites found in file.')
        return data['sites']

def check_site(site, username, if_found, if_not_found, if_neither):
    url = site['check_uri'].replace("{account}", username)
    try:
        resp_code = web_call_response_code(url)
        code_match = resp_code == int(site['account_existence_code'])

        resp_html_source = web_call_html_source(url)
        string_match = resp_html_source.find(site['account_existence_string']) > 0

        if debug_mode:
            if code_match:
                positive(f'HTTP status (match {code_match}): {resp_code}')
            else:
                negative(f'HTTP status (match {code_match}): {resp_code}')
            if string_match:
                positive(f'HTTP response (match: {string_match}). HTML source suppressed.')
            else:
                negative(f'HTTP response (match: {string_match}): {resp_html_source}')

        if code_match and string_match:
            COUNTER['FOUND'] += 1
            return if_found(url)

        code_missing_match = resp_code == int(site['account_missing_code'])
        string_missing_match = resp_html_source.find(site['account_missing_string']) > 0

        if code_missing_match or string_missing_match:
            COUNTER['NOT_FOUND'] += 1
            return if_not_found(url)

        COUNTER['ERROR'] += 1
        return if_neither(url)

    except Exception as caught:
        COUNTER['ERROR'] += 1
        error(f'Error when looking up {url} ({str(caught)})')

def positive_hit(url):
    positive(f'User found at {url}')
    running_positives.append(url)

###################
# Main
###################

def main():
    startstop('--------------------------------')
    startstop('')
    startstop('Starting the WhatsMyName Checking Script')

    args = parser.parse_args()

    if args.debug:
        global debug_mode
        debug_mode = args.debug
        neutral('Debug output enabled')

    if args.useragent:
        HEADERS['User-Agent'] = user_agent
        neutral(f'Custom UserAgent enabled. Using {user_agent}')

    # Add this in case user presses CTRL-C
    signal.signal(signal.SIGINT, signal_handler)

    # Read in the JSON file
    if (args.inputfile):
        input_file = args.inputfile
    else:
        input_file = 'web_accounts_list.json'

    with open(input_file) as data_file:
        data = json.load(data_file)

    sites_to_check = find_sites_to_check(args, data)

    try:
        for site in sites_to_check:
            if not site['valid']:
                warn(f'Skipping {site["name"]} - Marked as not valid.')
                continue

                # INSERT THREADING HERE?
                '''    x = threading.Thread(target=check_site, args=(site_, args.username), daemon=True)
                    threads.append(x)

                for thread in threads:
                    thread.start()

                for thread in threads:
                    thread.join()'''

            if args.username:
                check_site(site, args.username,
                           if_found     = lambda url: positive_hit(url),
                           if_not_found = lambda url: negative( f'User not found at {url}'),
                           if_neither   = lambda url: error(f'The check implementation is broken for {url}'))
            else:
                if args.debug:
                    debug(f'Checking {site["name"]}')
                    
                # Run through known accounts from the JSON
                for known_account in site['known_accounts']:
                    check_site(site, known_account,
                               if_found     = lambda url: positive(f'    As expected, profile found at {url}'),
                               if_not_found = lambda url: warn(  f'Profile not found at {url}'),
                               if_neither   = lambda url: error(  f'Neither conditions matched for {url}'))
                
                # Create a random string to be used for the "nonexistent" user and see what the site does
                non_existent = ''.join(random.choice(string.ascii_lowercase + string.ascii_uppercase + string.digits) for x in range(10))
                check_site(site, non_existent,
                           if_found     = lambda url: warn(  f'False positive for {url} from non-existent check'),
                           if_not_found = lambda url: positive(f'    As expected, no user found at {url} from non-existent check'),
                           if_neither   = lambda url: error(  f'Neither conditions matched for {url} from non-existent check'))

    finally:
        if COUNTER['FOUND'] and args.username:
            startstop('')
            startstop('Processing completed')
            positive(f'{COUNTER["FOUND"]} sites found')
            timestamp = time.strftime('%Y%m%d_%H%M%S', time.localtime())
            outputfile = f'{timestamp}_{args.username}.txt'
            with open(outputfile, 'w') as f:
                for positive_url in sorted(running_positives):
                    positive(f'    {positive_url}')
                    f.write(f'{positive_url}\n')
            positive(f'    The URLs where the username was found were exported to file: {outputfile}')

        if COUNTER['ERROR']:
            error(f'{COUNTER["ERROR"]} errors encountered')
            startstop('')
            startstop('Script completed')
            startstop('')
            startstop('--------------------------------')
            startstop('')
            sys.exit(2)

    startstop('')
    if COUNTER['FOUND'] == 0:
        warn('Script completed and no positive results were found.')
    else:
        startstop('Script completed')
    
    # Remove Gecko log
    #if os.path.isfile('geckodriver.log'):
     #   os.remove('geckodriver.log')

    startstop('--------------------------------')
    startstop('')

if __name__ == "__main__":
    # execute only if run as a script
    main()