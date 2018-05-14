#!/bin/bash

# This GUI bash script uses Zenity to pop up a window and ask for a username

USER=$(zenity --entry --text="Enter username")
python3 ./web_accounts_list_checker.py -u $USER
