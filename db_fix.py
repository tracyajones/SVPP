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

def import_data_file(input_dir):

    csvdata = []
    for dir_entry in os.listdir(input_dir):
        if dir_entry.endswith('.csv'):
            dir_entry_path = os.path.join(input_dir, dir_entry)
            if os.path.isfile(dir_entry_path):
                with open(dir_entry_path, 'rb') as csvfile:
                    reader = csv.DictReader(csvfile)
                    for row in reader:
                        print(row['Name'], row['Place of Employment'])
                        firstname = row['Name'].split(' ')[0]
                        lastname = row['Name'].split(' ')[1]
                        csvdata.append({'contactFirstname': firstname.strip(),
                                        'contactLastname': lastname.strip(),
                                        'contactCompany': row['Place of Employment'].strip()})
    return csvdata


def update_work(updated_company_list, rg_data, csv_data):
#   TODO: optimize this looping code to something more pythonic
    for rg in rg_data:
        for csv in csv_data:
            if csv['contactCompany'] != '':
                if rg['contactLastname'] == csv['contactLastname']:
                    # TODO: not finding my own name...  something is wrong
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

def store_data(output_file, csv_data):
    with open(output_file, 'w') as csvfile:
        fieldnames = ['first_name', 'last_name', 'company']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

        writer.writeheader()
        for item in csv_data:
            writer.writerow({'first_name': item['contactFirstname'],
                            'last_name': item['contactLastname'],
                            'company': item['contactCompany']})

def main(argv):

    parser = OptionParser()
    parser.add_option("-d", "--dir", dest="input_dir",
                  help="Directory which contains the CSV files to import")
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

    if options.input_dir is None or options.username is None or options.password is None or options.account is None:
        parser.error("Missing arguments")
        sys.exit(1)

    (token, tokenHash) = utils.login(options.username, options.password,
                                options.account)
    if token is None:
        sys.exit(1)

    data = import_data_file(options.input_dir)
    updated_company_list = merge_contacts(token, tokenHash, data)
    if updated_company_list is not None:
        store_data(os.path.join(options.input_dir, options.output_file), updated_company_list)

if __name__ == "__main__":
    main(sys.argv[1:])
