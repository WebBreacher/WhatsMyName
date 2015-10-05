'''
    Author : Micah Hoffman (@WebBreacher)
    Description : Takes each username from the web_accounts_list.json file and performs the lookup to see if the discovery determinator is still valid
'''
from pprint import pprint
import requests
import json
import os
import random
import datetime
import string

# Set HTTP Header info.
headers = {'User-Agent' : 'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2228.0 Safari/537.36'}

# Main
# Read in the JSON file
with open('web_accounts_list.json') as data_file:    
    data = json.load(data_file)
print '[-] We have %s sites that we will check.' % len(data['sites'])
#pprint(data)

# for each JSON entry
for site in data['sites'] :
	# Examine the current validity of the entry
	if site['valid'] == False:
		print '[!] Skipping %s as it is marked as not valid.' % site['name']
		break

	# Perform initial lookup
	# Pull the first user from known_accounts and replace the {account} with it
	url = site['check_uri'].replace("{account}", site['known_accounts'][0])
	print '[-] Looking up %s' % url
	# Make web request for that URL
	r = requests.get(url, headers = headers)
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
		print '     [+] Response code and Search Strings match expected.'
		# Generate a random string to use in place of known_accounts
		not_there_string = ''.join(random.choice(string.ascii_lowercase + string.ascii_uppercase + string.digits) for x in range(20))
		url_fp = site['check_uri'].replace("{account}", not_there_string)
		
		# False positive checking
		print '     [-] Checking for False Positives. Looking up %s' % url_fp
		r_fp = requests.get(url_fp, headers = headers)
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
			valid = False
		else:
			print '     [+] Passed false positives test.'
			print '     [+] Comments added: %s - Validated via script' % datetime.datetime.now()
			#site['comments'].append = '%s - Validated via script' % datetime.now()
		
	# If yes, 
		# Mark valid == True
		# Update the comments to note it was successfully verified on the date/time
	# If no,
		# does the "missing" string and code work?
			# If yes, then bad test user account
				# Mark valid == True
				# Update comments to note bad test user account
			# If no, then site issues
				# Mark valid == False
				# Update comments to note bad discovery string
	# Look for false positives
		# Make request for does-not-exist-#{rand(1000000000000)}"
			# If yes, then then site issues
				# Mark valid == False
				# Update comments to note bad discovery string
