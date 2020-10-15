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

def rer(ds_json):
    new_ds_json = {}
    for key in ds_json.keys():
        if ds_json[key].get("Value") is not None:
            new_ds_json[dcm_dict[int(key, 16)][4]] = ds_json[key]["Value"]

    return new_ds_json

def get_dicom_files_list(output_dir):
    return [join(output_dir,f) for f in listdir(output_dir) if isfile(join(output_dir, f))]

def dicom2json(dataset_files):
    dicom_files = []
    for filename in dataset_files:
        ds = pydicom.dcmread(filename)
        del ds.PixelData
        
        ds_json = ds.to_json_dict()
        new_ds_json = {}

        for key in ds_json.keys():
            try:
                if ds_json[key].get("Value") is not None:
                    new_ds_json[dcm_dict[int(key, 16)][4]] = (ds_json[key]["Value"][0] if len(ds_json[key]["Value"]) == 1 else ds_json[key]["Value"])
            except:
                pass

        dicom_files.append(new_ds_json)

    return dicom_files

def insert_objects(dicom_json_objects):
    mongo = MongoClient(MONGO_HOST, MONGO_PORT, username=MONGO_USER, password=MONGO_PASSWORD)
    #mongo = MongoClient('localhost', 27017)
    db = mongo.DicoogleDatabase
    collection = db.DicoogleObjs

    deltaT = time.time_ns()
    result = collection.insert_many(dicom_json_objects)
    deltaT = time.time_ns() - deltaT

    return { 'elapsed': deltaT/1e6, 'count':len(result.inserted_ids) }



def main(argv):
    output_dir = 'dataset'
    number_of_files = 0

    try:
        opts, args = getopt.getopt(argv,"hg:o:",["ifile=","output="])
    except getopt.GetoptError:
        print('insert.py -i <number of DICOM files to generate> -o <output_directory>')
        sys.exit(2)

    for opt, arg in opts:
        if opt == '-h':
            print('insert.py -g <number of DICOM files to generate> -o <output_directory>')
            sys.exit()
        elif opt in ("-g", "--generate"):
            try:
                number_of_files = int(arg)
            except ValueError:
                sys.exit("-g | --generate argument must be integer. Program will not run.")
        elif opt in ("-o", "--output"):
            output_dir = arg

    if number_of_files > 0:
        generate_dicom_files(output_dir, number_of_files)
    
    dataset_file_list = get_dicom_files_list(output_dir)
    dicom_json_objects = dicom2json(dataset_file_list)
    result = insert_objects(dicom_json_objects)

    print("Inserted %d objects in %.2f milisseconds.\n" % (result['count'], result['elapsed']))

if __name__ == "__main__":
   main(sys.argv[1:])