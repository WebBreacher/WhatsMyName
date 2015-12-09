#!/usr/bin/env python

'''
    Author : Micah Hoffman (@WebBreacher)
    Description : Takes each username from the web_accounts_list.json file and performs the lookup to see if the
                  discovery determinator is still valid

    TODO - 
    	1 - Make it so the script will toggle validity factor per entry and write to output file
    	2 - Make it so the script will append comment to the entry and output to file
    	3 - Colorize output
    	4 - Make a stub file shows last time sites were checked and problems.

    ISSUES -
    	1 - Had an issue with SSL handshakes and this script. Had to do the following to get it working
    		[From https://github.com/kennethreitz/requests/issues/2022]
    		# sudo apt-get install libffi-dev
			# pip install pyOpenSSL ndg-httpsclient pyasn1
'''
import requests
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
headers = {'User-Agent' : 'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2228.0'}
overall_results = {}

def signal_handler(signal, frame):
        print('[!!!] You pressed Ctrl+C. Exitting script.')
        FinalOutput()
        sys.exit(0)

def FinalOutput():
	if len(overall_results) > 0:
		print '------------'
		print 'The following previously "valid" sites had errors:'
		for site, results in overall_results.iteritems():
			print '     %s --> %s' % (site, results)
	else:
		print ":) No problems with the JSON file were found."

###################
# Main
###################
signal.signal(signal.SIGINT, signal_handler)
# Read in the JSON file
with open('web_accounts_list.json') as data_file:    
    data = json.load(data_file)
print '[-] %s sites found in file.' % len(data['sites'])

for site in data['sites'] :
	code_match, string_match = False, False
	# Examine the current validity of the entry
	if site['valid'] == False:
		print '[!] Skipping %s - Marked as not valid.' % site['name']
		continue
	if site['known_accounts'][0] == False:
		print '[!] Skipping %s - No valid user names to test.' % site['name']
		continue

	# Perform initial lookup
	# Pull the first user from known_accounts and replace the {account} with it
	url = site['check_uri'].replace("{account}", site['known_accounts'][0])
	print '[-] Looking up %s' % url
	try:
		# Make web request for that URL, timeout in X secs and don't verify SSL/TLS certs
		r = requests.get(url, headers=headers, timeout=30, verify=False)
	except requests.exceptions.Timeout:
    	print '     [!] ERROR: CONNECTION TIME OUT. Try increasing the timeout delay.'
    	continue
	except requests.exceptions.TooManyRedirects:
	    print '     [!] ERROR: TOO MANY REDIRECTS. Try changing the URL.'
    	continue
	except requests.exceptions.RequestException as e:
	    print '     [!] ERROR: CRITICAL ERROR. %s' % e
	    sys.exit(1)

	# Analyze the responses against what they should be
	if r.status_code == int(site['account_existence_code']):
		code_match = True
	else:
		code_match = False
	if r.text.find(site['account_existence_string']) > 0:
		string_match = True
	else:
		string_match = False
	
	if code_match == True and string_match == True:
		#print '     [+] Response code and Search Strings match expected.'
		# Generate a random string to use in place of known_accounts
		not_there_string = ''.join(random.choice(string.ascii_lowercase + string.ascii_uppercase + string.digits) for x in range(20))
		url_fp = site['check_uri'].replace("{account}", not_there_string)
		
		try:
			# False positive checking
			#print '     [-] Checking for False Positives. Looking up %s' % url_fp
			r_fp = requests.get(url_fp, headers=headers, timeout=30, verify=False)
		except requests.exceptions.Timeout:
	    	print '     [!] ERROR: CONNECTION TIME OUT. Try increasing the timeout delay in FP Check.'
	    	continue
		except requests.exceptions.TooManyRedirects:
		    print '     [!] ERROR: TOO MANY REDIRECTS. Try changing the URL in FP Check.'
	    	continue
		except requests.exceptions.RequestException as e:
		    print '     [!] ERROR: CRITICAL ERROR FP. %s' % e
		    sys.exit(1)

		if r_fp.status_code == int(site['account_existence_code']):
			code_match = True
		else:
			code_match = False
		if r_fp.text.find(site['account_existence_string']) > 0:
			string_match = True
		else:
			string_match = False
		if code_match == True and string_match == True:
			print '     [-] Code: %s; String: %s' % (code_match, string_match)
			print '     [!] ERROR: FALSE POSITIVE DETECTED. Response code and Search Strings match expected.'
			#TODO set site['valid'] = False
			overall_results[site['name']] = 'False Positive'
		else:
			#print '     [+] Passed false positives test.'
			pass
	elif code_match == True and string_match == False:
		#TODO set site['valid'] = False
		print '     [!] ERROR: BAD DETECTION STRING. "%s" was not found on resulting page.' % site['account_existence_string']
		overall_results[site['name']] = 'Bad detection string.'
	elif code_match == False and string_match == True:
		#TODO set site['valid'] = False
		print '     [!] ERROR: BAD DETECTION RESPONSE CODE. HTTP Response code different than expected.'
		overall_results[site['name']] = 'Bad detection code. Expected: %s; Received: %s.' % (str(r.status_code), site['account_existence_code'])
	else:
		#TODO set site['valid'] = False
		print '     [!] ERROR: BAD CODE AND STRING. Neither the HTTP response code or detection string worked.'
		overall_results[site['name']] = 'Bad detection code and string. Expected Code: %s; Received Code: %s.' % (str(r.status_code), site['account_existence_code'])

FinalOutput()
