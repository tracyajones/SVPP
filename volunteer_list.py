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
    r = requests.post('https://api.rescuegroups.org/http/v2.json', data = json.dumps(login_data))
    if r.status_code == 200:
        content = json.loads(r.content)
        if content['status'] == 'ok':
            return (content['data']['token'], content['data']['tokenHash'])
        else:
            print content['message']
    else:
        print r.text
    return (None, None)


def get_volunteers(token, tokenHash, csv_data):

    start = 0
    limit = 100
    updated_company_list = []
    while (1):
        data = {
                "token" : token,
                "tokenHash" : tokenHash,
                "objectType" : "contacts",
                "objectAction" : "search",
                "search" :  {
                        "resultStart" : start,
                        "resultLimit" : limit,
                        "resultSort" : "contactLastname",
                        "resultOrder" : "asc",
                        "fields" : [ "contactFirstname","contactLastname",
                                     "contactEmail", "contactCompany", "contactGroups"]
                }
            }
        r = requests.post('https://api.rescuegroups.org/http/v2.json', data = json.dumps(data))
        if r.status_code == 200:
            content = json.loads(r.content)
            if content['status'] == 'ok':
                for key,val in content['data'].items():
                    if 'Jones' in val['contactLastname']:
                        print val
                    if 'Volunteer' in val['contactGroups']:
                        csv_data.append(val)
                start += limit
                if start > int(content['foundRows']):
                    return csv_data
            else:
                print content['messages']
                return
        else:
            print r.text
            return

def store_data(output_file, csv_data):
    with open(output_file, 'w') as csvfile:
        fieldnames = ['first_name', 'last_name', 'email', 'company']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

        writer.writeheader()
        for item in csv_data:
            writer.writerow({'first_name': item['contactFirstname'],
                            'last_name': item['contactLastname'],
                            'email': item['contactEmail'],
                            'company': item['contactCompany']})

def main(argv):

    parser = OptionParser()
    parser.add_option("-o", "--outputfile", dest='output_file',
                  help="CSV file to export the data into",
                      default='export_data.csv')
    parser.add_option("-u", "--username", dest='username',
                  help="RG username")
    parser.add_option("-p", "--password", dest='password',
                  help="RG password")
    parser.add_option("-a", "--account", dest='account',
                  help="RG account")

    (options, args) = parser.parse_args()

    if options.username is None or options.password is None or options.account is None:
        parser.error("Missing arguments")
        sys.exit(1)

    (token, tokenHash) = login(options.username, options.password, options.account)
    if token is None:
        sys.exit(1)

    data = []
    volunteer_list = get_volunteers(token, tokenHash, data)
    if volunteer_list is not None:
        store_data(options.output_file, volunteer_list)

if __name__ == "__main__":
    main(sys.argv[1:])
