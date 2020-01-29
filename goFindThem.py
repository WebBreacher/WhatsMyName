'''
Created on Jan 22, 2020

@author: Micah Hoffman (@webBreacher) 
    Modified Micah's app to work within a wxPython GUI
    Added saved results to userResults.csv for easy confirmation - BG
    Modified the code to colour the output text based on returned results
    Added basic threading to handle the url requests
'''

import requests
import json
import os
import random
import string
import codecs
import configParams
import urllib3
import csv 
import concurrent.futures
import wx


from urllib3.exceptions import InsecureRequestWarning

from pubsub import pub # passing messages to the text edit widget

headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:70.0) Gecko/20100101 Firefox/70.0'}

urllib3.disable_warnings(InsecureRequestWarning)

def check_os():
    if os.name == "nt":
        operating_system = "windows"
    if os.name == "posix":
        operating_system = "posix"
    return operating_system

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
            self.GREEN = '(12,133,35)'
            self.YELLOW = ''
            self.RED = ''
            self.ENDC = ''
            
                #print("unicode error [x] output._output")
                #pub.sendMessage('O.Change', fobj = "unicode error [x] output._output")
                
                
class searchUsers():
    def __init__(self):
        overall_results = {}
        
        def web_call(location):
            try:
        # Make web request for that URL, timeout in X secs and don't verify SSL/TLS certs
                r = requests.get(location, headers=headers, timeout=30, verify=False)
                wx.Yield()  # allow process to yield back to main
            except requests.exceptions.Timeout:
                configParams.bcolour = 'RED'
                return '      ! ERROR: CONNECTION TIME OUT. Try increasing the timeout delay.'
            except requests.exceptions.TooManyRedirects:
                configParams.bcolour = 'RED'
                return '      ! ERROR: TOO MANY REDIRECTS. Try changing the URL.'
            except requests.exceptions.RequestException as e:
                configParams.bcolour = 'RED'
                return '      ! ERROR: CRITICAL ERROR. %s' % e
            else:
                configParams.bcolour = 'ENDC'
                return r

        with open('web_accounts_list.json') as data_file:
            data = json.load(data_file)
        
        # store successful username locates to CSV file
        
        outFile = open('userResults.csv', 'w', newline='')
        outputWriter = csv.writer(outFile)
        #  The meat of the program    
        for site in data['sites']:
            code_match, string_match = False, False
        # Examine the current validity of the entry
            if not site['valid']:
                configParams.bcolour = 'CYAN'
                pub.sendMessage('O.Change', fobj = ' *  Skipping %s - Marked as not valid.' % site['name'])
                configParams.bcolour = 'ENDC'
                continue
            if not site['known_accounts'][0]:
                configParams.bcolour = 'CYAN'
                pub.sendMessage('O.Change', fojb = ' *  Skipping %s - No valid user names to test.' % site['name'])
                configParams.bcolour = 'ENDC'
                continue

    # Perform initial lookup
    # Pull the first user from known_accounts and replace the {account} with it
            url_list = []
#    if args.username:
            if configParams.srchUserName:
                url = site['check_uri'].replace("{account}", configParams.srchUserName) # args.username)
                url_list.append(url)
                uname = configParams.srchUserName # args.username
            else:
                account_list = site['known_accounts']
                for each in account_list:
                    url = site['check_uri'].replace("{account}", each)
                    url_list.append(url)
                    uname = each
            for each in url_list:
                configParams.bcolour = 'ENDC'
                pub.sendMessage('O.Change', fobj = " -  Looking up %s" % each)
                r = web_call(each)
                if isinstance(r, str):
            # We got an error on the web call
                    pub.sendMessage('O.Change', fobj = r)
                    continue

                if configParams.debug: # args.debug:
                    pub.sendMessage('O.Change', fobj = "- HTTP status: %s" % r.status_code)
                    pub.sendMessage('O.Change', fobj = "- HTTP response: %s" % r.content)
        # Analyze the responses against what they should be
                if r.status_code == int(site['account_existence_code']):
                    code_match = True
                else:
                    code_match = False
                if r.text.find(site['account_existence_string']) > 0:
                    string_match = True
                else:
                    string_match = False

                if configParams.srchUserName: # args.username:
                    if code_match and string_match:
                        configParams.bcolour = 'GREEN'
                        pub.sendMessage('O.Change', fobj = '[+] Found user at %s' % each)
                        configParams.bcolour = 'ENDC'
                        outputWriter.writerow([each]) # update CSV file with results
                            
                continue

                if code_match and string_match:
            # Generate a random string to use in place of known_accounts
                    not_there_string = ''.join(random.choice(string.ascii_lowercase + string.ascii_uppercase + string.digits)
                                               for x in range(20))
                    url_fp = site['check_uri'].replace("{account}", not_there_string)
                    r_fp = web_call(url_fp)
                    if isinstance(r_fp, str):
                # If this is a string then web got an error
                        pub.sendMessage('O.Change', fobj = r_fp)
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
                        configParams.bcolour = 'RED'
                        pub.sendMessage('O.Change', fobj = '      -  Code: %s; String: %s' % (code_match, string_match))
                        pub.sendMessage('O.Change', fobj = '      !  ERROR: FALSE POSITIVE DETECTED. Response code and Search Strings match ' \
                                        'expected.')
                        #configParams.bcolour = 'ENDC'
                # TODO set site['valid'] = False
                        overall_results[site['name']] = 'False Positive'
                    else:
                        pass
                elif code_match and not string_match:
            # TODO set site['valid'] = False
                    configParams.bcolour = 'RED'
                    pub.sendMessage('O.Change', fobj = '      !  ERROR: BAD DETECTION STRING. "%s" was not found on resulting page.' \
                                % site['account_existence_string'])
                    overall_results[site['name']] = 'Bad detection string.'
                    if configParams.stringerror: # args.stringerror:
                        file_name = 'se-' + site['name'] + '.' + uname
                # Unicode sucks 
                        file_name = file_name.encode('ascii', 'ignore').decode('ascii')
                        error_file = codecs.open(file_name, 'w', 'utf-8')
                        error_file.write(r.text)
                        pub.sendMessage('O.Change', fobj = 'Raw data exported to file:' + file_name)
                        error_file.close()

                    elif not code_match and string_match:
            # TODO set site['valid'] = False
                        configParams.bcolour = 'RED'
                        pub.sendMessage('O.Change', fobj = '      !  ERROR: BAD DETECTION RESPONSE CODE. HTTP Response code different than ' \
                                'expected.')
                        #configParams.bcolour = 'ENDC'
                        overall_results[site['name']] = 'Bad detection code. Received Code: %s; Expected Code: %s.' % \
                            (str(r.status_code), site['account_existence_code'])
                    else:
            # TODO set site['valid'] = False
                        configParams.bcolour = 'RED'
                        pub.sendMessage('O.Change', fobj = '      !  ERROR: BAD CODE AND STRING. Neither the HTTP response code or detection ' \
                                'string worked.')
                        #configParams.bcolour = 'ENDC'
                        overall_results[site['name']] = 'Bad detection code and string. Received Code: %s; Expected Code: %s.' \
                            % (str(r.status_code), site['account_existence_code'])
                            
        def finaloutput():
            if len(overall_results) > 0:
                pub.sendMessage('O.Change', fobj = '---------------')
                pub.sendMessage('O.Change', fobj = 'The following previously "valid" sites had errors:')
            for site, results in sorted(overall_results.items()):
                configParams.bcolour = 'YELLOW'
                pub.sendMessage('O.Change', fobj = '     %s --> %s' % (site, results))
                configParams.bcolour = 'ENDC'
            else:
                pub.sendMessage('O.Change', fobj = ':) No problems with the JSON file were found.')

        if not configParams.srchUserName: # args.username:
            finaloutput()    
    
            # Threading 
    
if __name__ == "__goFindThem__":
    srchUsers = searchUsers()
    with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
        for index in range(10):
            executor.submit(srchUsers.web_call)
        
        
        
        
        
        
        
        
        