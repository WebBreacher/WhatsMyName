#!/usr/bin/python

"""
    Author : Micah Hoffman (@WebBreacher)
    Description : Takes each username from the web_accounts_list.json file and performs the lookup to see if the discovery entry is still valid
"""
import argparse
import codecs
from datetime import datetime
import json
import os
import random
import signal
import string
import sys
import time

import requests
import urllib3
import threading
import logging


##########################
#        Logging        #
##########################

# Set logging formatting
logging.basicConfig(level=logging.INFO, format='%(message)s')

##########################
# Variables && Functions #
##########################

# Set HTTP Header info.
headers = {'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
           'Accept-Language': 'en-US,en;q=0.5',
           'Accept-Encoding': 'gzip, deflate'
           }

all_found_sites = []

# Parse command line input
parser = argparse.ArgumentParser(description="This standalone script will look up a single "
                                             "username using the JSON file or will run a check"
                                             "of the JSON file for bad detection strings.")
parser.add_argument('-d', '--debug', help="Enable debug output", action="store_true")
parser.add_argument('-o', '--output', help="Create text output file", action="store_true",
                    default=False)
parser.add_argument('-of', '--outputfile', nargs='?', help="[OPTIONAL] Create text output file")
parser.add_argument('-in', '--inputfile', nargs='?', help="[OPTIONAL] Uses a specified file for checking the websites")
parser.add_argument('-s', '--site', nargs='*', help='[OPTIONAL] If this parameter is passed'
                    'the script will check only the named site or list of sites.')
parser.add_argument('-c', '--category', nargs='*', help='[OPTIONAL] If this parameter is passed'
                    'the script will check only the category or list of categories.')
parser.add_argument('-se', '--stringerror', help="Creates a site by site file for files that do"
                    "not match strings. Filenames will be 'se-(sitename).(username)",
                    action="store_true", default=False)
parser.add_argument('-u', '--username', help='[OPTIONAL] If this param is passed then this script'
                    'will perform the lookups against the given user name instead of running'
                    'checks against the JSON file.')


args = parser.parse_args()


if args.debug:
    logging.debug('Debug output enabled')

# Create the final results dictionary
overall_results = {}
username_results = []


def check_os():
    """
    # check operating system or adjust output color formatting
    :return: operating_system
    """
    # set default operating system to windows
    operating_system = "windows"

    if os.name == "posix":
        operating_system = "posix"
    return operating_system


#
# Class for colors
#
class Bcolors:
    # if os is windows or something like that then define colors as nothing
    CYAN = ''
    GREEN = ''
    YELLOW = ''
    RED = ''
    ENDC = ''

    # if os is linux or something like that then define colors as following
    if check_os() == "posix":
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


def signal_handler(*_):
    """
    If user pressed Ctrl+C close all connections and exit
    """
    logging.warning(Bcolors.RED + ' !!!  You pressed Ctrl+C. Exiting script.' + Bcolors.ENDC)
    finaloutput()
    sys.exit(130)


def web_call(location):
    try:
        # Make web request for that URL, timeout in X secs and don't verify SSL/TLS certs
        resp = requests.get(location, headers=headers, timeout=60, verify=False, allow_redirects=False)
    except requests.exceptions.Timeout:
        return f' !  ERROR: {location} CONNECTION TIME OUT. Try increasing the timeout delay.'
    except requests.exceptions.TooManyRedirects:
        return f' !  ERROR: {location} TOO MANY REDIRECTS. Try changing the URL.'
    except requests.exceptions.RequestException as e:
        return f' !  ERROR: CRITICAL ERROR. {e}'
    else:
        return resp


def random_string(length):
    return ''.join(
        random.choice(string.ascii_lowercase + string.ascii_uppercase + string.digits) for x in range(length))


def finaloutput():
    print('\n-------------------------------------------')

    if args.username:
        print(f'Searching for sites with username ({args.username}) > Found {len(username_results)} results:\n')
        for result in username_results:
            print(result)
    else:
        if len(overall_results) > 0:
            print('The following previously "valid" sites had errors:')
            for site_with_error, results in sorted(overall_results.items()):
                print(Bcolors.YELLOW + '     %s --> %s' % (site_with_error, results) + Bcolors.ENDC)
        else:
            print(':) No problems with the JSON file were found.')


# Suppress HTTPS warnings
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

###################
#      Main       #
###################

# Add this in case user presses CTRL-C
signal.signal(signal.SIGINT, signal_handler)

# Read in the JSON file
if (args.inputfile):
    inputfile = args.inputfile
else:
    inputfile = 'web_accounts_list.json'

with open(inputfile, 'r', errors='ignore') as data_file:
    data = json.load(data_file)

if args.site:
    # cut the list of sites down to only the requested ones
    args.site = [x.lower() for x in args.site]
    data['sites'] = [x for x in data['sites'] if x['name'].lower() in args.site]
    if len(data['sites']) == 0:
        logging.error(' -  Sorry, the requested site or sites were not found in the list')
        sys.exit(1)
    sites_not_found = len(args.site) - len(data['sites'])
    if sites_not_found:
        logging.warning(' -  WARNING: %d requested sites were not found in the list' % sites_not_found)
    logging.info(' -  Checking %d sites' % len(data['sites']))
elif args.category:
    # cut the list of sites down by category
    args.category = [x.lower() for x in args.category]
    data['sites'] = [x for x in data['sites'] if x['category'].lower() in args.category]
    if len(data['sites']) == 0:
        logging.error(' -  Sorry, no sites were found for the requested category or categories')
        sys.exit(1)
    logging.info(' -  Checking %d sites' % len(data['sites']))
else:
    logging.info(' -  %s sites found in file.' % len(data['sites']))

def check_site(site, username=None):
    # Examine the current validity of the entry
    if not site['valid']:
        return logging.info(f"{Bcolors.CYAN} *  Skipping {site['name']} - Marked as not valid.{Bcolors.ENDC}")

    if not site['known_accounts'][0]:
        return logging.info(f"{Bcolors.CYAN} *  Skipping {site['name']} - No valid user names to test.{Bcolors.ENDC}")

    # Set the username
    if username:
        uname = username
    else:
        # if no username specified Pull the first user from known_accounts and replace the {account} with it
        known_account = site['known_accounts'][0]
        uname = known_account

    url = site['check_uri'].replace("{account}", uname)

    # Perform initial lookup
    logging.info(f" >  Looking up {url}")
    r = web_call(url)
    if isinstance(r, str):
        # We got an error on the web call
        return logging.error(Bcolors.RED + r + Bcolors.ENDC)
    else:
        # Check debug mode and print error to console
        if args.debug:
            logging.debug("- HTTP status: %s" % r.status_code)
            logging.debug("- HTTP response: %s" % r.content)

        # Analyze the responses against what they should be
        code_match = r.status_code == int(site['account_existence_code'])
        if site['account_existence_string']:
            string_match = r.text.find(site['account_existence_string']) >= 0
        else:
            string_match = 0

        if username:
            if code_match and string_match:
                username_results.append(Bcolors.GREEN + '[+] Found user at %s' % url + Bcolors.ENDC)
                all_found_sites.append(url)
                return
        else:
            if code_match and string_match:
                # logging.info('     [+] Response code and Search Strings match expected.')
                # Generate a random string to use in place of known_accounts
                url_fp = site['check_uri'].replace("{account}", random_string(20))
                r_fp = web_call(url_fp)
                if isinstance(r_fp, str):
                    # If this is a string then web got an error
                    return logging.error(r_fp)

                code_match = r_fp.status_code == int(site['account_existence_code'])
                string_match = r_fp.text.find(site['account_existence_string']) > 0

                if code_match and string_match:
                    logging.info('      -  Code: %s; String: %s' % (code_match, string_match))
                    logging.error(
                        Bcolors.RED + f' !  ERROR: {site} FALSE POSITIVE DETECTED. Response code and Search '
                                      f'Strings match expected.' + Bcolors.ENDC + '\r')
                    # TODO set site['valid'] = False
                    overall_results[site['name']] = 'False Positive'
                else:
                    # logging.info('     [+] Passed false positives test.')
                    pass
            elif code_match and not string_match:
                # TODO set site['valid'] = False
                logging.error(
                    Bcolors.RED + f' !  ERROR: {site} BAD DETECTION STRING. "{site["account_existence_string"]}" '
                                  f'was not found on resulting page.' + Bcolors.ENDC)
                overall_results[site['name']] = 'Bad detection string.'
                if args.stringerror:
                    file_name = 'se-' + site['name'] + '.' + uname
                    # Unicode sucks
                    file_name = file_name.encode('ascii', 'ignore').decode('ascii')
                    error_file = codecs.open(file_name, 'w', 'utf-8')
                    error_file.write(r.text)
                    logging.info('Raw data exported to file:' + file_name)
                    error_file.close()

            elif not code_match and string_match:
                # TODO set site['valid'] = False
                logging.error(Bcolors.RED + f' !  ERROR: {site} BAD DETECTION RESPONSE CODE. HTTP Response code '
                                            f'different than expected.' + Bcolors.ENDC + '\r')
                overall_results[site['name']] = 'Bad detection code. Received Code: %s; Expected Code: %s.' % \
                                                (str(r.status_code), site['account_existence_code'])
            else:
                # TODO set site['valid'] = False
                logging.error(
                    Bcolors.RED + f' !  ERROR: {site} BAD CODE AND STRING. Neither the HTTP response code or '
                                  f'detection string worked.' + Bcolors.ENDC + '\r')
                overall_results[site['name']] = 'Bad detection code and string. Received Code: %s; Expected Code: %s.' \
                                                % (str(r.status_code), site['account_existence_code'])


if __name__ == "__main__":
    # Start threads
    threads = []

    start_time = datetime.utcnow()
    for site_ in data['sites']:
        x = threading.Thread(target=check_site, args=(site_, args.username), daemon=True)
        threads.append(x)

    for thread in threads:
        thread.start()

    for thread in threads:
        thread.join()

    # Print result
    finaloutput()

    if args.username and all_found_sites:
        if (args.output or args.outputfile):
            if (args.outputfile):
                outfile = args.outputfile
            else:
                outfile = '{}_{}.txt'.format(str(int(time.time())), args.username)
            with open(outfile, 'w') as f:
                for item in all_found_sites:
                    f.write("%s\n" % item)
            print('\nRaw data exported to file: ' + outfile)

    # Print how long it took
    #end_time = datetime.utcnow()
    #iff = end_time - start_time
    #logging.info(f'\nFinished in {diff}')
