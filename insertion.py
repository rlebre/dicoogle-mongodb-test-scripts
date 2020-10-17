#!/usr/bin/python

import sys, getopt

import pydicom
from pydicom._dicom_dict import DicomDictionary as dcm_dict

import time
from pymongo import MongoClient
from generator import generate_dicom_files, generate_dicom_to_json
from local_settings import *
import json

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

def dicom2json(filename):
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

    return new_ds_json

def insert_objects(mongo_connection, dicom_paths):
    db = mongo_connection.DicoogleDatabase
    collection = db.DicoogleObjs

    dicom_json_objects = []
    for dicom in dicom_paths:
        dicom_json_objects.append(dicom2json(dicom))

    deltaT = time.time_ns()
    result = collection.insert_many(dicom_json_objects)
    deltaT = time.time_ns() - deltaT

    return { 'elapsed': deltaT/1e6, 'count':len(result.inserted_ids) }

def insert_json_objects(mongo_connection, dicom_paths):
    db = mongo_connection.DicoogleDatabase
    collection = db.DicoogleObjs

    dicom_json_objects = []  
    for dicom_path in dicom_paths:
        with open(dicom_path) as f:
            dicom_json = json.load(f)
            dicom_json_objects.append(dicom_json)

    deltaT = time.time_ns()
    result = collection.insert_many(dicom_json_objects)
    deltaT = time.time_ns() - deltaT

    return { 'elapsed': deltaT/1e6, 'count':len(result.inserted_ids) }

def insert_objects_by_chuncks(mongo_connection, dicom_json_objects, chunk_size=5000):
    dicom_objects_chunk = []
    results = { 'elapsed': 0.0, 'count': 0 }

    for idx, dicom_json_obj in enumerate(dicom_json_objects):
        dicom_objects_chunk.append(dicom_json_obj)

        if len(dicom_objects_chunk) % chunk_size == 0:
            statistics = insert_objects(mongo_connection, dicom_objects_chunk)
            results['elapsed'] += statistics['elapsed']
            results['count'] += statistics['count']
            dicom_objects_chunk = []
        
    if len(dicom_objects_chunk) < chunk_size and len(dicom_objects_chunk) > 0:
        statistics = insert_objects(mongo_connection, dicom_objects_chunk)
        results['elapsed'] += statistics['elapsed']
        results['count'] += statistics['count']

    return results

def insert_json_objects_by_chuncks(mongo_connection, dicom_json_objects, chunk_size=5000):
    dicom_objects_chunk = []
    results = { 'elapsed': 0.0, 'count': 0 }

    for idx, dicom_json_obj in enumerate(dicom_json_objects):
        dicom_objects_chunk.append(dicom_json_obj)

        print('{:2.2%} - {}/{}'.format((idx / len(dicom_json_objects)), idx, len(dicom_json_objects)), sep=" ", end="\r", flush=True)
       
        if len(dicom_objects_chunk) % chunk_size == 0:
            statistics = insert_json_objects(mongo_connection, dicom_objects_chunk)
            results['elapsed'] += statistics['elapsed']
            results['count'] += statistics['count']
            dicom_objects_chunk = []
        
    if len(dicom_objects_chunk) < chunk_size and len(dicom_objects_chunk) > 0:
        statistics = insert_json_objects(mongo_connection, dicom_objects_chunk)
        results['elapsed'] += statistics['elapsed']
        results['count'] += statistics['count']

    return results

def main(argv):
    output_dir = 'dataset'
    number_of_files = 0
    generate_in_dicom = True
    mongo_connection = MongoClient(MONGO_HOST, MONGO_PORT, username=MONGO_USER, password=MONGO_PASSWORD)
    #mongo_connection = MongoClient('localhost', 27017)
    chunk_size = 0

    try:
        opts, args = getopt.getopt(argv,"hg:o:c:j",["ifile=","output="])
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
        elif opt in ("-j", "--json"):
            try:
                generate_in_dicom = False
            except ValueError:
                sys.exit("-j | --json argument must be integer. Program will not run.")
        elif opt in ("-o", "--output"):
            output_dir = arg
        elif opt in ("-c", "--chunk"):
            try:
                chunk_size = int(arg)
            except ValueError:
                sys.exit("-c | --chunk argument must be integer. Program will not run.")

    if number_of_files > 0 and generate_in_dicom == True:
        generate_dicom_files(output_dir, number_of_files)
    elif number_of_files > 0 and generate_in_dicom == False:
        generate_dicom_to_json(output_dir, number_of_files)
    
    dataset_file_list = get_dicom_files_list(output_dir)
    #dicom_json_objects = dicom2json(dataset_file_list)

    if chunk_size == 0 and generate_in_dicom == True:
        result = insert_objects(mongo_connection, dataset_file_list)
    elif chunk_size > 0 and generate_in_dicom == True:
        result = insert_objects_by_chuncks(mongo_connection, dataset_file_list, chunk_size)
    elif chunk_size == 0 and generate_in_dicom == False:
        result = insert_json_objects(mongo_connection, dataset_file_list)
    elif chunk_size > 0 and generate_in_dicom == False:
        result = insert_json_objects_by_chuncks(mongo_connection, dataset_file_list, chunk_size)


    print("Inserted %d objects in %.2f milisseconds.\n" % (result['count'], result['elapsed']))

    mongo_connection.close()

if __name__ == "__main__":
   main(sys.argv[1:])