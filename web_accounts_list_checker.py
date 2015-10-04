'''
    Author : Micah Hoffman (@WebBreacher)
    Description : Takes each username from the web_accounts_list.json file and performs the lookup to see if the discovery determinator is still valid
'''

import requests
import json
import os
import urllib

# Main

# Read in the JSON file
# for each JSON entry
# Perform lookup
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

