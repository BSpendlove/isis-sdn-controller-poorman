#!/usr/bin/env python
import json
import os
import requests
import env_file
from sys import stdin, stdout

def message_parser(line):
    temp_message = json.loads(line)

    return temp_message

api_details = env_file.get(path="/exabgp/env/api")
api_url = api_details["flask_api"]

counter = 0
while True:
    try:
        line = stdin.readline().strip()
        
        # When the parent dies we are seeing continual newlines, so we only access so many before stopping
        if line == "":
            counter += 1
            if counter > 100:
                break
            continue
        counter = 0
        
        # Parse message, and if it's the correct type, store in the database
        message = message_parser(line)
        if message:
            if message["type"] == "state":
                requests.post("{}/exabgp/state".format(api_url), json=message)
            if message["type"] == "update":
                requests.post("{}/exabgp/update".format(api_url), json=message)

    except KeyboardInterrupt:
        pass
    except IOError:
        # most likely a signal during readline
        pass
