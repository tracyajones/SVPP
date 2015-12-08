#!/usr/bin/python

__author__ = 'tjones'

import csv
import json
from optparse import OptionParser
import pprint
import requests
import sys

pp = pprint.PrettyPrinter()

def import_data_file(inputfile):
    with open(inputfile, 'rb') as csvfile:
        reader = csv.DictReader(csvfile)
        csvdata = []
        for row in reader:
            print(row['Name'], row['Place of Employment'])
            firstname = row['Name'].split(' ')[0]
            lastname = row['Name'].split(' ')[1]
            csvdata.append({'contactFirstname': firstname, 'contactLastname': lastname, 'contactCompany': row['Place of Employment']})
    return csvdata

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

def update_work(updated_company_list, rg_data, csv_data):
#   TODO: optimize this looping code to something more pythonic
    for rg in rg_data:
        for csv in csv_data:
            if csv['contactCompany'] != '':
                if rg['contactLastname'] == csv['contactLastname']:
                    # TODO: not finding my own name...  something is wrong
                    if rg['contactLastname'].lower() == 'jones':
                        print 'FOUND IT'
                    if rg['contactFirstname'] == csv['contactFirstname']:
                        if rg['contactCompany'] != csv['contactCompany']:
                            rg['contactCompany'] = csv['contactCompany']
                            updated_company_list.append(rg)

def merge_contacts(token, tokenHash, csv_data):

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
                        "fields" : [ "contactID","contactFirstname","contactLastname","contactCompany"]
                }
            }
        r = requests.post('https://api.rescuegroups.org/http/v2.json', data = json.dumps(data))
        if r.status_code == 200:
            content = json.loads(r.content)
            if content['status'] == 'ok':
                for key,val in content['data'].items():
                    pp.pprint(val)
                update_work(updated_company_list, content['data'].values(), csv_data)
                start += limit
                if start > int(content['foundRows']):
                    return updated_company_list
            else:
                print content['message']
                return
        else:
            print r.text
            return

def main(argv):

    parser = OptionParser()
    parser.add_option("-i", "--inputfile", dest="inputfile",
                  help="CSV file which contains the data to import")
    parser.add_option("-u", "--username", dest='username',
                  help="RG username")
    parser.add_option("-p", "--password", dest='password',
                  help="RG password")
    parser.add_option("-a", "--account", dest='account',
                  help="RG account")

    (options, args) = parser.parse_args()

    if options.inputfile is None or options.username is None or options.password is None or options.account is None:
        parser.error("Missing arguments")
        sys.exit(1)

    (token, tokenHash) = login(options.username, options.password, options.account)
    if token is None:
        sys.exit(1)

    data = import_data_file(options.inputfile)
    updated_company_list = merge_contacts(token, tokenHash, data)
    pp.pprint(updated_company_list)


if __name__ == "__main__":
    main(sys.argv[1:])
