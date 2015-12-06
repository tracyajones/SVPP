#!/usr/bin/python

__author__ = 'tjones'

import csv
import sys, getopt


def import_data_file(inputfile):
    with open(inputfile, 'rb') as csvfile:
        filereader = csv.reader(csvfile, delimiter=',', quotechar='|')
        for row in filereader:
            print ', '.join(row)
    return None


def main(argv):
    inputfile = ''
    outputfile = ''
    try:
        opts, args = getopt.getopt(argv, "hi:o:", ["ifile=", "ofile="])
    except getopt.GetoptError:
        print 'db_fix.py -i <inputfile> -o <outputfile>'
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-h':
            print 'test.py -i <inputfile> -o <outputfile>'
            sys.exit()
        elif opt in ("-i", "--ifile"):
            inputfile = arg
        elif opt in ("-o", "--ofile"):
            outputfile = arg
    print 'Input file is "', inputfile
    print 'Output file is "', outputfile

    data = import_data_file(inputfile)

if __name__ == "__main__":
    main(sys.argv[1:])
