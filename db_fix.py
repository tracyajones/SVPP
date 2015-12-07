#!/usr/bin/python

__author__ = 'tjones'

import csv
import json
from optparse import OptionParser
import pprint
import requests
import sys


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

def update_work(rg_data, csv_data):
    merged_dict = dict(rg_data, **csv_data)
    print merged_dict
    #for key,val in rg_data.items():
    #    if val['contactLastname'] in csv_data['contactLastname']:
    #        print val

def get_contacts(token, tokenHash, csv_data):

    start = 0
    limit = 50
    pp = pprint.PrettyPrinter()
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
                update_work(content['data'], csv_data)
                start += limit
                if start > content['foundRows']:
                    return
            else:
                print content['message']
                return
        else:
            print r.text
            return

    return None

def main(argv):
    key = 'QP4f2HO9'

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
        sys.exit(0)

    print 'Input file is ', options.inputfile
    print 'username is ', options.username
    print 'password is ', options.password
    print 'account is ', options.account

    (token, tokenHash) = login(options.username, options.password, options.account)
    if token is None:
        sys.exit(2)
    print token, tokenHash
    data = import_data_file(options.inputfile)
    get_contacts(token, tokenHash, data)



if __name__ == "__main__":
    main(sys.argv[1:])
