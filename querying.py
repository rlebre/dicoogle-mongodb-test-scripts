#!/usr/bin/python

import sys, getopt

import pydicom
from pydicom._dicom_dict import DicomDictionary as dcm_dict

import time
from pymongo import MongoClient
from generator import generate_dicom_files
from local_settings import *

from os import listdir
from os.path import isfile, join
import json

def create_indexes_dim(mongo_connection):
    db = mongo_connection.DicoogleDatabase
    collection = db.DicoogleObjs

    collection.create_index("PatientID")
    collection.create_index("PatientName")
    collection.create_index("StudyInstanceUID")
    collection.create_index("SeriesInstanceUID")
    collection.create_index("SOPInstanceUID")

def drop_indexes_dim(mongo_connection):
    db = mongo_connection.DicoogleDatabase
    collection = db.DicoogleObjs

    try:
        collection.drop_index("PatientID_1")
    except:
        pass

    try:
        collection.drop_index("PatientName_1")
    except:
        pass

    try:
        collection.drop_index("StudyInstanceUID_1")
    except:
        pass

    try:
        collection.drop_index("SeriesInstanceUID_1")
    except:
        pass

    try:
        collection.drop_index("SOPInstanceUID_1")
    except:
        pass

def query(mongo_connection, q, times=1):
    db = mongo_connection.DicoogleDatabase
    collection = db.DicoogleObjs

    total_delta = 0
    last_result = None
    for i in range(times):
        deltaT = time.time_ns()
        result = collection.count_documents(q)
        deltaT = time.time_ns() - deltaT
        total_delta += deltaT
        last_result = result

    return { 'elapsed': deltaT/1e6, 'repeated': times, 'average': deltaT/1e6/times, 'results': last_result }


def main(argv):
    mongo = MongoClient(MONGO_HOST, MONGO_PORT, username=MONGO_USER, password=MONGO_PASSWORD)
    #mongo = MongoClient('localhost', 27017)
    q = {}

    try:
        opts, args = getopt.getopt(argv,"hidq:",["query="])
    except getopt.GetoptError:
        print('insert.py [-i] -q <query>')
        sys.exit(2)

    for opt, arg in opts:
        if opt == '-h':
            print('insert.py [-i] [-d] -q <query>')
            sys.exit()
        elif opt in ("-i", "--indexes"):
            create_indexes_dim(mongo)
        elif opt in ("-d", "--delete_indexes"):
            drop_indexes_dim(mongo)
        elif opt in ("-q", "--query"):
            q = json.loads(arg)
        
    results = query(mongo, q, 10)
    
    print("Elapsed %.2fms." % results['elapsed'])
    print("Repeated %d times." % results['repeated'])
    print("Average per query %.2fms." % results['average'])
    print("Result count: %d.\n" % results['results'])

    mongo.close()

if __name__ == "__main__":
   main(sys.argv[1:])