'''
    Author : Micah Hoffman (@WebBreacher)
    Description : Takes each username from the web_accounts_list.json file and performs the lookup to see if the discovery determinator is still valid
'''
from pprint import pprint
import requests
import json
import os
import urllib

# Main
# Read in the JSON file
with open('web_accounts_list.json') as data_file:    
    data = json.load(data_file)
print '[-] We have %s sites that we will check.' % len(data['sites'])
#pprint(data)

# for each JSON entry
for site in data['sites'] :
	#pprint (site)
	
	# Perform lookup
	# Pull the first user from known_accounts and replace the {account} with it
	url = site['check_uri'].replace("{account}", site['known_accounts'][0])
	print '[-] Looking up %s' % url
	# Make web request for that URL
	
	# Analyze if lookup was successful
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
'''