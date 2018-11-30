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


def get_animal_id(token, tokenHash, animal_name, animal_species):
    limit = 10
    data = {
        "token": token,
        "tokenHash": tokenHash,

        "objectType": "animals",
        "objectAction": "search",
        "search":
            {
                "resultStart": 0,
                "resultLimit": limit,
                "resultSort": "animalID",
                "resultOrder": "asc",
                "filters":
                    [
                        {
                            "fieldName": "animalStatus",
                            "operation": "equals",
                            "criteria": "hold"
                        },
                        {
                            "fieldName": "animalSpecies",
                            "operation": "equals",
                            "criteria": animal_species
                        },
                        {
                            "fieldName": "animalName",
                            "operation": "equals",
                            "criteria": animal_name
                        },
                    ],
                "filterProcessing": "3",
                "fields":
                    [
                        "animalID", "animalName", "animalStatus",
                        "animalSpecies"]
            }
    }

    def process_data(content, data):
        if content['foundRows'] != '1':
            print 'Found multiple matches'
            for key, val in content['data'].items():
                print key, val
            return
        else:
            for key, val in content['data'].items():
                print key, val
                data.append(key)
                return data

    return get_data(data, process_data, limit)

def get_file_list(token, tokenHash, id):
    limit = 50

    data = {
        "token": token,
        "tokenHash": tokenHash,

        "objectType": "animalFiles",
        "objectAction": "search",
        "search":
            {
                "resultStart": 0,
                "resultLimit": limit,
                "resultSort": "animalfileID",
                "resultOrder": "asc",
                "filters":
                    [
                        {
                            "fieldName": "animalfileAnimalID",
                            "operation": "equals",
                            "criteria": id
                        },
                     ],
                "filterProcessing": "1",
                "fields":
                    [
                        "animalfileID",
                        "animalfileAnimalID",
                        "animalfileOldName",
                        "animalfileDescription",
                        "animalfileStatus",
                        "animalfileDisplayInline",
                        "animalfilePublic",
                        "animalfileSize",
                        "animalfileCreatedDate", ]
            }
    }

    def process_data(content, file_list):
        for key, val in content['data'].items():
            if val['animalfileOldName'].lower().find('internal') == -1:
                file_list.append(val['animalfileID'])
        return file_list

    return get_data(data, process_data, limit)


# def get_file(token, tokenHash, file_id):
#     start = 0
#     limit = 50
#     while (1):
#         data = {
#             "token": token,
#             "tokenHash": tokenHash,
#
#             "objectType": "animalFiles",
#             "objectAction": "view",
#             "values":
#                 [
#                     {
#                         "animalfileID": file_id
#                     }
#
#                 ],
#             "fields": ["animalfileID", "animalfileAnimalID",
#                        "animalfileOldName", "animalfileDescription",
#                        "animalfileStatus", "animalfileDisplayInline",
#                        "animalfileSize", "animalfileCreatedDate"]
#         }
#
#         r = requests.post('https://api.rescuegroups.org/http/v2.json',
#                           data=json.dumps(data))
#         if r.status_code == 200:
#             content = json.loads(r.content)
#             if content['status'] == 'ok':
#                 file_list = []
#                 for key, val in content['data'].items():
#                     if val['animalfileOldName'].lower().find('internal') == -1:
#                         file_list.append(val['animalfileID'])
#                     #print key, val
#                 start += limit
#                 if start > int(content['foundRows']):
#                     return file_list
#             else:
#                 print content['messages']
#                 return
#         else:
#             print r.text
#             return

def show_data(token, tokenHash):
    start = 0
    limit = 100

    data = {
        "token": token,
        "tokenHash": tokenHash,
        "objectType": "volunteersJournalEntries",
        "objectAction": "search",
        "search": {
            "resultStart": start,
            "resultLimit": limit,
            "resultSort": "volunteerName",
            "resultOrder": "asc",
            "fields": ["volunteerName", "journalEntryComment"]
        }
    }
    get_data(data, processor_func=None, verbose=True)


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
    parser.add_option("-n", "--name", dest='name',
                      help="Animal Name")
    parser.add_option("-s", "--species", dest='species',
                      help="Animal Species")

    (options, args) = parser.parse_args()

    if options.username is None or options.password is None or \
                    options.account is None or options.name is None or \
                    options.species is None:
        parser.error("Missing arguments")
        sys.exit(1)

    (token, tokenHash) = login(options.username, options.password,
                               options.account)
    if token is None:
        sys.exit(1)

    pp =  pprint.PrettyPrinter(indent=4)
    id = get_animal_id(token, tokenHash, options.name, options.species)
    if id is not None:
        print id
        file_list = get_file_list(token, tokenHash, id)
        pp.pprint(file_list)
    #    for file in file_list:
    #        get_file(token, tokenHash, file)
    #    if volunteer_list is not None:
    #         store_data(options.output_file, volunteer_list)

    show_data(token, tokenHash)




if __name__ == "__main__":
    main(sys.argv[1:])
