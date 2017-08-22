#!/usr/bin/python

import requests
import argparse
import json
import random
import string
import signal
import sys
import codecs
import pkg_resources
from .b_colors import Bcolors
from requests.packages.urllib3.exceptions import InsecureRequestWarning


class WebAccountsListChecker():
    """
    Author : Micah Hoffman (@WebBreacher)
    Description : Takes each username from the web_accounts_list.json file and
                  performs the lookup to see if the
                  discovery determinator is still valid

    TODO :
                   1 - Make it so the script will toggle validity factor per
                       entry and write to output file
                   2 - Make it so the script will append comment to the entry
                       and output to file
                   3 - Make a stub file shows last time sites were checked
                       and problems.

    ISSUES -
                   1 - Had an issue with SSL handshakes and this script.
                       Had to do the following to get it working
                       [From https://github.com/kennethreitz/requests/issues/2022]
                       # sudo apt-get install libffi-dev
                       # pip install pyOpenSSL ndg-httpsclient pyasn1 requests
    """
    headers = {}
    overall_results = {}
    data = {}
    args = {}
    terminal_colors = {}

    def __init__(self):
        """
        Set the header and grab the params
        passed in to arg parse from command
        line
        """
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) '
            'Chrome/45.0.2454.93 Safari/537.36'}

        parser = argparse.ArgumentParser(
            description="This standalone script will look up a single username using the JSON file"
            " or will run a check of the JSON file for bad detection strings.")
        parser.add_argument(
            '-u',
            '--username',
            help='[OPTIONAL] If this param is passed then this script will perform the '
            'lookups against the given user name instead of running checks against '
            'the JSON file.')
        parser.add_argument(
            '-se',
            '--stringerror',
            help="Creates a site by site file for files that do not match strings. Filenames will be 'se-(sitename).(username)",
            action="store_true",
            default=False)
        parser.add_argument(
            '-s',
            '--site',
            nargs='*',
            help='[OPTIONAL] If this parameter is passed the script will check only the named site or list of sites.')
        self.args = parser.parse_args()
        self.terminal_colors = Bcolors()


    def run(self):
        """
        Grab the JSON data and start
        process
        """
        print "Running"
        signal.signal(signal.SIGINT, self.signal_handler)
        requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

        self.data = json.load(self.get_json_file())
        if self.args.site:
            self.process_sites()
        else:
            print ' -  %s sites found in file.' % len(self.data['sites'])
            self.check_valid_and_known()

        if not self.args.username:
            self.final_output()

    def get_json_file(self):
        """
        Get the static JSON file from the
        packages static directory
        """
        resource_package = __name__  # Could be any module/package name
        resource_path = '/'.join(('json', 'web_accounts_list.json'))
        return pkg_resources.resource_stream(resource_package, resource_path)

    def process_sites(self):
        """
        Cut the list of sites down
        to only the requested ones
        """
        sites = [x.lower() for x in self.args.site]
        self.data['sites'] = [
            x for x in self.data['sites'] if x['name'].lower() in sites]

        if len(self.data['sites']) == 0:
            print ' -  Sorry, the requested site or sites were not found in the list'
            sys.exit()

        sites_not_found = len(sites) - len(self.data['sites'])
        if sites_not_found:
            print ' -  WARNING: %d requested sites were not found in the list' % sites_not_found
        else:
            print ' -  Checking %d sites' % len(self.data['sites'])
            self.check_valid_and_known()

    def check_valid_and_known(self):
        """
        Examine the current
        validity of the entry
        """
        for site in self.data['sites']:
            if not site['valid']:
                print self.terminal_colors.CYAN + ' *  Skipping %s - Marked as not valid.' % site['name'] + self.terminal_colors.ENDC
                continue
            if not site['known_accounts'][0]:
                print self.terminal_colors.CYAN + ' *  Skipping %s - No valid user names to test.' % site['name'] + self.terminal_colors.ENDC
                continue

            self.process_user_name(site)

    def process_user_name(self, site):
        """
        Perform initial lookup
        Pull the first user from known_accounts and replace the {account} with it
        """
        url_list = []

        if self.args.username:
            url = site['check_uri'].replace("{account}", self.args.username)
            url_list.append(url)
            uname = self.args.username
        else:
            account_list = site['known_accounts']
            for each in account_list:
                url = site['check_uri'].replace("{account}", each)
                url_list.append(url)
                uname = each

        for url in url_list:
            self.process_url_list(url, site)

    def process_url_list(self, url, site):
        """
        process the URL passed to
        method
        """
        code_match = False
        string_match = False

        print ' -  Looking up %s' % url
        r = self.web_call(url)
        if isinstance(r, str):
            print r
            return

        if r.status_code == int(site['account_existence_code']):
            code_match = True

        if r.text.find(site['account_existence_string']) > 0:
            string_match = True

        if code_match and string_match:
            if self.args.username:
                print self.terminal_colors.GREEN + '[+] Found user at %s' % url + self.terminal_colors.ENDC

            self.check_account_exists(site)
        elif code_match and not string_match:

            print self.terminal_colors.RED + '      !  ERROR: BAD DETECTION STRING. "%s" was not found on resulting page.' \
                % site['account_existence_string'] + self.terminal_colors.ENDC
            self.overall_results[site['name']] = 'Bad detection string.'
            if self.args.stringerror:
                file_name = 'se-' + site['name'] + '.' + uname
                file_name = file_name.encode('ascii', 'ignore').decode('ascii')
                error_file = codecs.open(file_name, 'w', 'utf-8')
                error_file.write(r.text)
                print "Raw data exported to file:" + file_name
                error_file.close()
        elif not code_match and string_match:
            print self.terminal_colors.RED + '      !  ERROR: BAD DETECTION RESPONSE CODE. HTTP Response code different than ' \
                'expected.' + self.terminal_colors.ENDC
            self.overall_results[site['name']] = 'Bad detection code. Received Code: %s; Expected Code: %s.' % (
                str(r.status_code), site['account_existence_code'])
        else:
            print self.terminal_colors.RED + '      !  ERROR: BAD CODE AND STRING. Neither the HTTP response code or detection ' \
                                'string worked.' + self.terminal_colors.ENDC
            self.overall_results[site['name']] = 'Bad detection code and string. Received Code: %s; Expected Code: %s.' \
                                            % (str(r.status_code), site['account_existence_code'])

    def check_account_exists(self, site):
        """
        print '     [+] Response code and Search Strings match expected.'
        Generate a random string to use in place of known_accounts
        """
        code_match = False
        string_match = False
        not_there_string = ''.join(
            random.choice(
                string.ascii_lowercase +
                string.ascii_uppercase +
                string.digits) for x in range(20))
        url_fp = site['check_uri'].replace("{account}", not_there_string)
        r_fp = self.web_call(url_fp)

        if isinstance(r_fp, str):
            print r_fp
            return

        if r_fp.status_code == int(site['account_existence_code']):
            code_match = True
        if r_fp.text.find(site['account_existence_string']) > 0:
            string_match = True

        if code_match and string_match:
            print '      -  Code: %s; String: %s' % (code_match, string_match)
            print self.terminal_colors.RED + '      !  ERROR: FALSE POSITIVE DETECTED. Response code and Search Strings match ' \
                'expected.' + self.terminal_colors.ENDC
            self.overall_results[site['name']] = 'False Positive'
        else:
            return

    def signal_handler(self, signal, frame):
        print(
            self.terminal_colors.RED +
            ' !!!  You pressed Ctrl+C. Exitting script.' +
            self.terminal_colors.ENDC)
        self.final_output()
        sys.exit(0)

    def web_call(self, location):
        """
        Make web request for that URL, timeout in X secs and don't verify
        SSL/TLS certs
        """
        try:
            r = requests.get(
                location,
                headers=self.headers,
                timeout=60,
                verify=False)
        except requests.exceptions.Timeout:
            return self.terminal_colors.RED + \
                '      ! ERROR: CONNECTION TIME OUT. Try increasing the timeout delay.' + self.terminal_colors.ENDC
        except requests.exceptions.TooManyRedirects:
            return self.terminal_colors.RED + \
                '      ! ERROR: TOO MANY REDIRECTS. Try changing the URL.' + self.terminal_colors.ENDC
        except requests.exceptions.RequestException as e:
            return self.terminal_colors.RED + '      ! ERROR: CRITICAL ERROR. %s' % e + self.terminal_colors.ENDC
        else:
            return r

    def final_output(self):
        """
        Print final output
        """
        if len(self.overall_results) > 0:
            print '------------'
            print 'The following previously "valid" sites had errors:'
            for site, results in sorted(self.overall_results.iteritems()):
                print self.terminal_colors.YELLOW + '     %s --> %s' % (site, results) + self.terminal_colors.ENDC
        else:
            print ":) No problems with the JSON file were found."
