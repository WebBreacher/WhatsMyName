#!/usr/bin/python

"""
    Author : Micah Hoffman (@WebBreacher)
    Description : Takes each username from the web_accounts_list.json file and performs the lookup to see if the entry is still valid
"""
import argparse
import codecs
import json
import random
import signal
import string
import sys
import time

import requests
from requests.packages.urllib3.exceptions import InsecureRequestWarning
from rich import print

###################
# Variables && Functions
###################
# Set HTTP Header info.
headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.75 Safari/537.36',
           'Accept' : 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
           'Accept-Language' : 'en-US,en;q=0.5',
           'Accept-Encoding' : 'gzip, deflate'
          }

# Create an empty list to hold the successful results
all_found_sites = []

# Parse command line input
parser = argparse.ArgumentParser(description="This standalone script will look up a single "
                                             "username using the JSON file or will run a check"
                                             "of the JSON file for bad detection strings.")
parser.add_argument('-d', '--debug', help="Enable debug output", action="store_true")
parser.add_argument('-o', '--output', help="Create text output file", action="store_true",
                    default=False)
parser.add_argument('-s', '--site', nargs='*', help='[OPTIONAL] If this parameter is passed'
                    'the script will check only the named site or list of sites.')
parser.add_argument('-se', '--stringerror', help="Creates a site by site file for files that do"
                    "not match strings. Filenames will be 'se-(sitename).(username)",
                    action="store_true", default=False)
parser.add_argument('-u', '--username', help='[OPTIONAL] If this param is passed then this script'
                    'will perform the lookups against the given user name instead of running'
                    'checks against the JSON file.')

args = parser.parse_args()

if args.debug:
    print('Debug output enabled')

# Create the final results dictionary
overall_results = {}


def signal_handler(*_):
    print('[bold red] !!!  You pressed Ctrl+C. Exiting script.[/bold red]')
    finaloutput()
    sys.exit(130)


def web_call(location):
    try:
        # Make web request for that URL, timeout in X secs and don't verify SSL/TLS certs
        resp = requests.get(location, headers=headers, timeout=60, verify=False, allow_redirects=False)
    except requests.exceptions.Timeout:
        return '[bold red]      ! ERROR: CONNECTION TIME OUT. Try increasing the timeout delay.[/bold red]'
    except requests.exceptions.TooManyRedirects:
        return '[bold red]      ! ERROR: TOO MANY REDIRECTS. Try changing the URL.[/bold red]'
    except requests.exceptions.RequestException as e:
        return '[bold red]      ! ERROR: CRITICAL ERROR. %s[/bold red]' % e 
    else:
        return resp


def random_string(length):
    return ''.join(random.choice(string.ascii_lowercase + string.ascii_uppercase + string.digits) for x in range(length))

def finaloutput():
    if len(overall_results) > 0:
        print('------------')
        print('The following previously "valid" sites had errors:')
        for site_with_error, results in sorted(overall_results.items()):
            print('[bold yellow]     %s --> %s[/bold yellow]' % (site_with_error, results))
    else:
        print(':) No problems with the JSON file were found.')


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

if args.site:
    # cut the list of sites down to only the requested ones
    args.site = [x.lower() for x in args.site]
    data['sites'] = [x for x in data['sites'] if x['name'].lower() in args.site]
    if len(data['sites']) == 0:
        print('[bold red] -  Sorry, the requested site or sites were not found in the list[/bold red]')
        sys.exit(1)
    sites_not_found = len(args.site) - len(data['sites'])
    if sites_not_found:
        print('[bold yellow] -  WARNING: %d requested sites were not found in the list[/bold yellow]' % sites_not_found)
    print('[bold cyan] -  Checking %d sites[/bold cyan]' % len(data['sites']))
else:
    print('[bold cyan] -  %s sites found in file.[/bold cyan]' % len(data['sites']))


for site in data['sites']:
    code_match, string_match = False, False
    # Examine the current validity of the entry
    if not site['valid']:
        print('[bold cyan] *  Skipping %s - Marked as not valid.[/bold cyan]' % site['name'])
        continue
    if not site['known_accounts'][0]:
        print('[bold cyan] *  Skipping %s - No valid user names to test.[/bold cyan]' % site['name'])
        continue

    # Perform initial lookup
    # Pull the first user from known_accounts and replace the {account} with it
    url_list = []
    if args.username:
        url = site['check_uri'].replace("{account}", args.username)
        url_list.append(url)
        uname = args.username
    else:
        account_list = site['known_accounts']
        for each in account_list:
            url = site['check_uri'].replace("{account}", each)
            url_list.append(url)
            uname = each
    for each in url_list:
        print('[bold cyan] -  Looking up %s[/bold cyan]' % each)
        r = web_call(each)
        if isinstance(r, str):
            # We got an error on the web call
            print(r)
            continue

        if args.debug:
            print("[bold cyan]- HTTP status: %s[/bold cyan]" % r.status_code)
            print("[bold cyan]- HTTP response: %s[bold cyan]" % r.content)

        # Analyze the responses against what they should be
        code_match = r.status_code == int(site['account_existence_code'])
        string_match = r.text.find(site['account_existence_string']) >= 0

        if args.username:
            if code_match and string_match:
                print('[bold green][+] Found user at %s[/bold green]' % each)
                all_found_sites.append(each)
            continue

        if code_match and string_match:
            # print('     [+] Response code and Search Strings match expected.')
            # Generate a random string to use in place of known_accounts
            url_fp = site['check_uri'].replace("{account}", random_string(20))
            r_fp = web_call(url_fp)
            if isinstance(r_fp, str):
                # If this is a string then web got an error
                print(r_fp)
                continue

            code_match = r_fp.status_code == int(site['account_existence_code'])
            string_match = r_fp.text.find(site['account_existence_string']) > 0

            if code_match and string_match:
                print('      -  Code: %s; String: %s' % (code_match, string_match))
                print('[bold red]      !  ERROR: FALSE POSITIVE DETECTED. Response code and Search Strings match ' \
                      'expected.[/bold red]')
                # TODO set site['valid'] = False
                overall_results[site['name']] = 'False Positive'
            else:
                # print('     [+] Passed false positives test.')
                pass
        elif code_match and not string_match:
            # TODO set site['valid'] = False
            print('[/bold red]      !  ERROR: BAD DETECTION STRING. "%s" was not found on resulting page.[/bold red]' \
                  % site['account_existence_string'])
            overall_results[site['name']] = 'Bad detection string.'
            if args.stringerror:
                file_name = 'se-' + site['name'] + '.' + uname
                # Unicode sucks
                file_name = file_name.encode('ascii', 'ignore').decode('ascii')
                error_file = codecs.open(file_name, 'w', 'utf-8')
                error_file.write(r.text)
                print('Raw data exported to file:' + file_name)
                error_file.close()

        elif not code_match and string_match:
            # TODO set site['valid'] = False
            print('[bold red]      !  ERROR: BAD DETECTION RESPONSE CODE. HTTP Response code different than ' \
                  'expected.[/bold red]')
            overall_results[site['name']] = 'Bad detection code. Received Code: %s; Expected Code: %s.' % \
                (str(r.status_code), site['account_existence_code'])
        else:
            # TODO set site['valid'] = False
            print('[bold red]      !  ERROR: BAD CODE AND STRING. Neither the HTTP response code or detection ' \
                  'string worked.[/bold red]')
            overall_results[site['name']] = 'Bad detection code and string. Received Code: %s; Expected Code: %s.' \
                % (str(r.status_code), site['account_existence_code'])

if not args.username:
    finaloutput()

if args.username and all_found_sites:
    if args.output:
        outfile = '{}_{}.txt'.format(str(int(time.time())), args.username)
        print(outfile)
        fh = open(outfile, 'w')
        fh.writelines(all_found_sites)
        print('Raw data exported to file:' + outfile)
        fh.close()
