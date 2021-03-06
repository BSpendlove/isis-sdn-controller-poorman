#!/usr/bin/env python
import logging
import json
import os
import requests
import env_file
from sys import stdin, stdout

logging.basicConfig(level=logging.DEBUG)

"""
This script will simply listen for the stdin stream and is attached to the JSON encoder as a process for ExaBGP.

A simply POST request is sent to some predefined Flask routes (sdncontroller) with 0 validation...
"""

def message_parser(line):
    temp_message = None
    try:
        temp_message = json.loads(line)
    except Exception as error:
        logging.debug("Error trying json.loads() on line: \n{}".format(line))
        logging.debug("Exception Error was: {}".format(error))
    return temp_message

api_details = env_file.get(path="/exabgp/env/api")
api_url = api_details["flask_api"]

counter = 0
while True:
    try:
        line = stdin.readline().strip()
        
        if line == "":
            counter += 1
            if counter > 100:
                break
            continue
        counter = 0
        
        message = message_parser(line)
        message_string = str(message)
        url = None
        if message:
            logging.debug("Message received from peer...\n{}".format(json.dumps(message)))
            if message["type"] == "state":
                if message["neighbor"]["state"] == "up":
                    # /exabgp/neighbor/state/up
                    url = "{}/exabgp/neighbor/state/up".format(api_url)
                if message["neighbor"]["state"] == "down":
                    # /exabgp/neighbor/state/down
                    url = "{}/exabgp/neighbor/state/down".format(api_url)
                if message["neighbor"]["state"] == "connected":
                    # /exabgp/neighbor/state/connected
                    url = "{}/exabgp/neighbor/state/connected".format(api_url)
            if message["type"] == "update":
                if "announce" in message_string:
                    if "bgpls-node" in message_string:
                        # /exabgp/update/bgpls/announce/node
                        url = "{}/exabgp/update/bgpls/announce/node".format(api_url)
                    if "bgpls-link" in message_string:
                        # /exabgp/update/bgpls/announce/link
                        url = "{}/exabgp/update/bgpls/announce/link".format(api_url)
                    if "bgpls-prefix-v4" in message_string:
                        # /exabgp/update/bgpls/announce/prefixv4
                        url = "{}/exabgp/update/bgpls/announce/prefixv4".format(api_url)
                    if "bgpls-prefix-v6" in message_string:
                        # /exabgp/update/bgpls/announce/prefixv6
                        url = "{}/exabgp/update/bgpls/announce/prefixv6".format(api_url)
                elif "withdraw" in message_string:
                    url = "{}/exabgp/update/bgpls/withdraw/all".format(api_url)
                    if "bgpls-node" in message_string:
                        # /exabgp/update/bgpls/withdraw/node
                        url = "{}/exabgp/update/bgpls/withdraw/node".format(api_url)
                    if "bgpls-link" in message_string:
                        # /exabgp/update/bgpls/withdraw/link
                        url = "{}/exabgp/update/bgpls/withdraw/link".format(api_url)
                    if "bgpls-prefix-v4" in message_string:
                        # /exabgp/update/bgpls/withdraw/prefixv4
                        url = "{}/exabgp/update/bgpls/withdraw/prefixv4".format(api_url)
                    if "bgpls-prefix-v6" in message_string:
                        # /exabgp/update/bgpls/withdraw/prefixv6
                        url = "{}/exabgp/update/bgpls/withdraw/prefixv6".format(api_url)
            if url:
                requests.post(url, json=message)

    except KeyboardInterrupt:
        pass
    except IOError:
        # most likely a signal during readline
        pass
