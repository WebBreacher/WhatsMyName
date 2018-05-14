#!/bin/bash

USER=$(zenity --entry --text="Enter username")
python3 ./web_accounts_list_checker.py -u $USER