#!/usr/bin/python

__author__ = 'tjones'

import csv
import json
from optparse import OptionParser
import os
import pprint
import requests
import sys
import utils

pp = pprint.PrettyPrinter()


def get_animals(token, tokenHash):
    start = 0
    limit = 1000

    data = {
        "token": token,
        "tokenHash": tokenHash,
        "objectType": "animals",
        "objectAction": "search",
        "search": {
            "resultStart": start,
            "resultLimit": limit,
            "resultSort": "animalName",
            "resultOrder": "asc",
            "fields": ["animalName", "animalID", "animalRescueID",
                       "animalUpdatedDate"],
        }
    }
    pets = utils.get_data(data, processor_func=None, start=start, \
                          limit=limit, verbose=True)

    print '\n\n-------\n\n'

    fix_list = [v for v in pets if (v['animalRescueID'].startswith('A') is \
                False and v['animalRescueID'] != 'Community')]
    print '\n\n%d items to fix\n\n' % len(fix_list)
    return fix_list


def fix_rescue_id(token, tokenHash, fix_list):
    for item in fix_list:
        if do_update(token, tokenHash, item) is False:
            return



def do_update(token, tokenHash, item):
    data = \
        {
            "token": token,
            "tokenHash": tokenHash,
            "objectType": "animals",
            "objectAction": "edit",
            "values":
                [
                    {
                        "animalID": item['animalID'],
                        "animalRescueID": "Community",
                    }
                ]
        }

    print 'Going to update %s %s %s' % (item['animalID'], item['animalName'],
                                     item['animalRescueID'])

    r = requests.post('https://api.rescuegroups.org/http/v2.json',
                      data=json.dumps(data))
    if r.status_code == 200:
        content = json.loads(r.content)
        if content['status'] != 'ok':
            print content['messages']
            return False
    else:
        print r.text
        return False


def main(argv):
    parser = OptionParser()
    parser.add_option("-u", "--username", dest='username',
                      help="RG username")
    parser.add_option("-p", "--password", dest='password',
                      help="RG password")
    parser.add_option("-a", "--account", dest='account',
                      help="RG account")

    (options, args) = parser.parse_args()

    if options.username is None or options.password is None or \
                    options.account is None:
        parser.error("Missing arguments")
        sys.exit(1)

    (token, tokenHash) = utils.login(options.username, options.password,
                                     options.account)
    if token is None:
        sys.exit(1)

    fix_list = get_animals(token, tokenHash)

    if len(fix_list) > 0:
        fix_rescue_id(token, tokenHash, fix_list)


if __name__ == "__main__":
    main(sys.argv[1:])
