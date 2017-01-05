#!/usr/bin/python

"""
    Author : Micah Hoffman (@WebBreacher)
    Description : Takes each username from the web_accounts_list.json file and performs the lookup to see if the
                  discovery determinator is still valid

    TODO -
        1 - Make it so the script will toggle validity factor per entry and write to output file
        2 - Make it so the script will append comment to the entry and output to file
        3 - Make a stub file shows last time sites were checked and problems.

    ISSUES -
        1 - Had an issue with SSL handshakes and this script. Had to do the following to get it working
            [From https://github.com/kennethreitz/requests/issues/2022]
            # sudo apt-get install libffi-dev
            # pip install pyOpenSSL ndg-httpsclient pyasn1 requests
"""
import requests
import argparse
from requests.packages.urllib3.exceptions import InsecureRequestWarning
import json
import os
import random
import datetime
import string
import signal
import sys

###################
# Variables && Functions
###################
# Set HTTP Header info.
headers = {'User-Agent' : 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) '
                          'Chrome/45.0.2454.93 Safari/537.36'}

# Parse command line input
parser = argparse.ArgumentParser(description="This standalone script will look up a single username using the JSON file"
                                             " or will run a check of the JSON file for bad detection strings.")
parser.add_argument('-u', '--username', help='[OPTIONAL] If this param is passed then this script will perform the '
                                             'lookups against the given user name instead of running checks against '
                                             'the JSON file.')
args = parser.parse_args()


# Create the final results dictionary
overall_results = {}


def check_os():
    if os.name == "nt":
        operating_system = "windows"
    if os.name == "posix":
        operating_system = "posix"
    return operating_system

#
# Class for colors
#
if check_os() == "posix":
    class bcolors:
        CYAN = '\033[96m'
        GREEN = '\033[92m'
        YELLOW = '\033[93m'
        RED = '\033[91m'
        ENDC = '\033[0m'

        def disable(self):
            self.CYAN = ''
            self.GREEN = ''
            self.YELLOW = ''
            self.RED = ''
            self.ENDC = ''

# if we are windows or something like that then define colors as nothing
else:
    class bcolors:
        CYAN = ''
        GREEN = ''
        YELLOW = ''
        RED = ''
        ENDC = ''

        def disable(self):
            self.CYAN = ''
            self.GREEN = ''
            self.YELLOW = ''
            self.RED = ''
            self.ENDC = ''


def signal_handler(signal, frame):
    print(bcolors.RED + ' !!!  You pressed Ctrl+C. Exitting script.' + bcolors.ENDC)
    finaloutput()
    sys.exit(0)


def web_call(url):
    try:
        # Make web request for that URL, timeout in X secs and don't verify SSL/TLS certs
        r = requests.get(url, headers=headers, timeout=60, verify=False)
    except requests.exceptions.Timeout:
        return bcolors.RED + '      ! ERROR: CONNECTION TIME OUT. Try increasing the timeout delay.' + bcolors.ENDC
    except requests.exceptions.TooManyRedirects:
        return bcolors.RED + '      ! ERROR: TOO MANY REDIRECTS. Try changing the URL.' + bcolors.ENDC
    except requests.exceptions.RequestException as e:
        return bcolors.RED + '      ! ERROR: CRITICAL ERROR. %s' % e + bcolors.ENDC
    else:
        return r


def finaloutput():
    if len(overall_results) > 0:
        print '------------'
        print 'The following previously "valid" sites had errors:'
        for site, results in sorted(overall_results.iteritems()):
            print bcolors.YELLOW + '     %s --> %s' % (site, results) + bcolors.ENDC
    else:
        print ":) No problems with the JSON file were found."

###################
# Main
###################

# Add this in case user presses CTRL-C
signal.signal(signal.SIGINT, signal_handler)

# Suppress HTTPS warnings
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

# Read in the JSON file
with open('web_accounts_list.json') as data_file:
    data = json.load(data_file)
print ' -  %s sites found in file.' % len(data['sites'])

for site in data['sites']:
    code_match, string_match = False, False
    # Examine the current validity of the entry
    if not site['valid']:
        print bcolors.CYAN + ' *  Skipping %s - Marked as not valid.' % site['name'] + bcolors.ENDC
        continue
    if not site['known_accounts'][0]:
        print bcolors.CYAN + ' *  Skipping %s - No valid user names to test.' % site['name'] + bcolors.ENDC
        continue

    # Perform initial lookup
    # Pull the first user from known_accounts and replace the {account} with it
    if args.username:
        url = site['check_uri'].replace("{account}", args.username)
    else:
        url = site['check_uri'].replace("{account}", site['known_accounts'][0])
        print ' -  Looking up %s' % url
    r = web_call(url)
    if isinstance(r, str):
        # We got an error on the web call
        print r
        continue

    # Analyze the responses against what they should be
    if r.status_code == int(site['account_existence_code']):
        code_match = True
    else:
        code_match = False
    if r.text.find(site['account_existence_string']) > 0:
        string_match = True
    else:
        string_match = False

    if args.username:
        if code_match and string_match:
            print ' -  Found user at %s' % url
        continue

    if code_match and string_match:
        # print '     [+] Response code and Search Strings match expected.'
        # Generate a random string to use in place of known_accounts
        not_there_string = ''.join(random.choice(string.ascii_lowercase + string.ascii_uppercase + string.digits)
                                   for x in range(20))
        url_fp = site['check_uri'].replace("{account}", not_there_string)
        r_fp = web_call(url_fp)
        if isinstance(r_fp, str):
            # If this is a string then web got an error
            print r_fp
            continue

        if r_fp.status_code == int(site['account_existence_code']):
            code_match = True
        else:
            code_match = False
        if r_fp.text.find(site['account_existence_string']) > 0:
            string_match = True
        else:
            string_match = False
        if code_match and string_match:
            print '      -  Code: %s; String: %s' % (code_match, string_match)
            print bcolors.RED + '      !  ERROR: FALSE POSITIVE DETECTED. Response code and Search Strings match ' \
                                'expected.' + bcolors.ENDC
            # TODO set site['valid'] = False
            overall_results[site['name']] = 'False Positive'
        else:
            # print '     [+] Passed false positives test.'
            pass
    elif code_match and not string_match:
        # TODO set site['valid'] = False
        print bcolors.RED + '      !  ERROR: BAD DETECTION STRING. "%s" was not found on resulting page.' % \
                            site['account_existence_string'] + bcolors.ENDC
        overall_results[site['name']] = 'Bad detection string.'
    elif not code_match and string_match:
        # TODO set site['valid'] = False
        print bcolors.RED + '      !  ERROR: BAD DETECTION RESPONSE CODE. HTTP Response code different than expected.' \
              + bcolors.ENDC
        overall_results[site['name']] = 'Bad detection code. Received Code: %s; Expected Code: %s.' % \
                                        (str(r.status_code), site['account_existence_code'])
    else:
        # TODO set site['valid'] = False
        print bcolors.RED + '      !  ERROR: BAD CODE AND STRING. Neither the HTTP response code or detection string ' \
                            'worked.' + bcolors.ENDC
        overall_results[site['name']] = 'Bad detection code and string. Received Code: %s; Expected Code: %s.' % \
                                        (str(r.status_code), site['account_existence_code'])

if not args.username:
    finaloutput()
