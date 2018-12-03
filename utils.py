#!/usr/bin/python

__author__ = 'tjones'

import csv
import json
from optparse import OptionParser
import os
import pprint
import requests
import sys

pp = pprint.PrettyPrinter()


def login(username, password, account):
    login_data = {
        "username": username,
        "password": password,
        "accountNumber": account,
        "action": "login"
    }

    print json.dumps(login_data)
    r = requests.post('https://api.rescuegroups.org/http/v2.json',
                      data=json.dumps(login_data))
    if r.status_code == 200:
        content = json.loads(r.content)
        if content['status'] == 'ok':
            return (content['data']['token'], content['data']['tokenHash'])
        else:
            print content['message']
    else:
        print r.text
    return (None, None)

def get_data(data, processor_func, start=0, limit=100, verbose=False):
    val = []
    printHeader = True
    while (1):
        r = requests.post('https://api.rescuegroups.org/http/v2.json',
                          data=json.dumps(data))
        if r.status_code == 200:
            content = json.loads(r.content)
            if content['status'] == 'ok':

                if processor_func is not None:
                    val = processor_func(content, val)
                else:
                    val = append_data(val, content['data'].items())

                if verbose:
                    if printHeader:
                        print ' total rows %d' % int(content['foundRows'])
                    for k, v in content['data'].items():
                        print k, v
                start += limit
                data['search']['resultStart'] = start
                if start >= int(content['foundRows']):
                    return val
            else:
                print content['messages']
                return
        else:
            print r.text
            return

def append_data(data, val):
    for k,v in val:
        data.append(v)
    return data