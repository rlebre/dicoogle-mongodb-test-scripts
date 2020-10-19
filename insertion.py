#!/usr/bin/python
# -*- coding: utf-8 -*-

__author__ = "Rui Lebre"
__credits__ = ["PyDicom", "DicomGenerator", "PyMongo"]
__license__ = "GPL"
__version__ = "0.1.0"
__maintainer__ = "Rui Lebre"
__email__ = "ruilebre@ua.pt"
__status__ = "Production"

import getopt
import json
import os
import sys
import time
from os import listdir
from os.path import isfile, join

from dicomgenerator.factory import CTDatasetFactory
from pydicom.datadict import keyword_for_tag
from pymongo import MongoClient

from local_settings import *


# def rer(ds_json):
#     new_ds_json = {}
#     for key in ds_json.keys():
#         if ds_json[key].get("Value") is not None:
#             new_ds_json[DicomDictionary[int(key, 16)][4]] = ds_json[key]["Value"]

#     return new_ds_json


def get_file_list(output_dir):
    return [join(output_dir, f) for f in listdir(output_dir) if isfile(join(output_dir, f))]


def merge_sum_dicts(dict1, dict2):
    return {k: dict1.get(k, 0) + dict2.get(k, 0) for k in set(dict1) | set(dict2)}


def read_json_files(dicom_paths):
    dicom_json_objects = []
    for dicom_path in dicom_paths:
        with open(dicom_path) as f:
            dicom_json = json.load(f)
            dicom_json_objects.append(dicom_json)
    return dicom_json_objects


def print_progress(current, total):
    print('{:2.2%} - {}/{}'.format((current / total), current, total), sep=" ", end="\r", flush=True)


def insert_list(mongo_connection, dicom_json_objects):
    db = mongo_connection.DicoogleDatabase
    collection = db.DicoogleObjs

    elapsed = time.time_ns()
    result = collection.insert_many(dicom_json_objects)
    elapsed = time.time_ns() - elapsed

    return {'elapsed': elapsed / 1e6, 'count': len(result.inserted_ids)}


def insert_path(mongo_connection, dicom_paths):
    dicom_json_objects = read_json_files(dicom_paths)

    return insert_list(mongo_connection, dicom_json_objects)


def insertion_objects(mongo_connection, number_of_objects, chunk_size=500):
    dicom_objects_chunk = []
    results = {}

    for idx in range(number_of_objects):
        print_progress(idx, len(number_of_objects))

        dcm_obj = CTDatasetFactory()
        del dcm_obj.PixelData
        json_obj = dcm_obj.to_json_dict()

        new_obj = {}
        for key in json_obj.keys():
            try:
                if json_obj[key].get("Value") is not None:
                    new_obj[keyword_for_tag(key)] = (
                        json_obj[key]["Value"][0] if len(json_obj[key]["Value"]) == 1 else json_obj[key]["Value"])
            except:
                pass

        dicom_objects_chunk.append(new_obj)

        if len(dicom_objects_chunk) % chunk_size == 0:
            statistics = insert_list(mongo_connection, dicom_objects_chunk)
            results = merge_sum_dicts(results, statistics)
            dicom_objects_chunk = []

    if chunk_size > len(dicom_objects_chunk) > 0:
        statistics = insert_list(mongo_connection, dicom_objects_chunk)
        results = merge_sum_dicts(results, statistics)

    return results


def insertion_dicom(mongo_connection, path_list, chunk_size=500):
    dicom_objects_chunk = []
    results = {'elapsed': 0.0, 'count': 0}

    for idx, dicom_json_obj in enumerate(path_list):
        print_progress(idx, len(path_list))
        dicom_objects_chunk.append(dicom_json_obj)

        if len(dicom_objects_chunk) % chunk_size == 0:
            statistics = insert_path(mongo_connection, dicom_objects_chunk)
            results = merge_sum_dicts(results, statistics)
            dicom_objects_chunk = []

    if chunk_size > len(dicom_objects_chunk) > 0:
        statistics = insert_path(mongo_connection, dicom_objects_chunk)
        results = merge_sum_dicts(results, statistics)

    return results


def insertion_json(mongo_connection, path_list, chunk_size=500):
    dicom_objects_chunk = []
    results = {'elapsed': 0.0, 'count': 0}

    for idx, dicom_json_obj in enumerate(path_list):
        print_progress(idx, len(path_list))

        dicom_objects_chunk.append(read_json_files(dicom_json_obj))

        if len(dicom_objects_chunk) % chunk_size == 0:
            statistics = insert_list(mongo_connection, dicom_objects_chunk)
            results = merge_sum_dicts(results, statistics)
            dicom_objects_chunk = []

    if chunk_size > len(dicom_objects_chunk) > 0:
        statistics = insert_list(mongo_connection, dicom_objects_chunk)
        results = merge_sum_dicts(results, statistics)

    return results


def main(argv):
    usage = 'insertion.py -n <number_of_objects_to_insert -c <chunk_size> -j/-d <dicom|json_directory>'
    input_dir = ''
    number_of_files = 0
    read_in_dicom = True
    mongo_connection = MongoClient(MONGO_HOST, MONGO_PORT, username=MONGO_USER, password=MONGO_PASSWORD)
    #mongo_connection = MongoClient('localhost', 27017)
    chunk_size = 1

    try:
        opts, args = getopt.getopt(argv, "hc:n:d:j:", ["chunk=", "number=", "dicom", "json"])
    except getopt.GetoptError:
        print(usage)
        sys.exit(1)

    for opt, arg in opts:
        if opt == '-h':
            print(usage)
            sys.exit(0)
        elif opt in ("-c", "--chunk"):
            try:
                chunk_size = int(arg)
            except ValueError:
                sys.exit("-c | --chunk argument must be integer. Program will not run.")
        elif opt in ("-n", "--number"):
            try:
                number_of_files = int(arg)
            except ValueError:
                sys.exit("-n | --number argument must be integer. Program will not run.")
        elif opt in ("-j", "--json"):
            read_in_dicom = False
            input_dir = arg
        elif opt in ("-d", "--dicom"):
            read_in_dicom = True
            input_dir = arg

    if number_of_files <= 0 or chunk_size < 1:
        sys.exit("You must define a positive number of files/objects/chunk_size. Program will not run.")

    if input_dir == "":
        result = insertion_objects(mongo_connection, number_of_files, chunk_size)
    else:
        if not os.access(input_dir, os.R_OK):
            sys.exit("You do not have writing permissions on output directory. Program will not run.")

        dataset_file_list = get_file_list(input_dir)

        if read_in_dicom:
            result = insertion_dicom(mongo_connection, dataset_file_list, chunk_size)
        else:
            result = insertion_json(mongo_connection, dataset_file_list, chunk_size)

    print("Inserted %d objects in %.2f milisseconds.\n" % (result['count'], result['elapsed']))

    mongo_connection.close()


if __name__ == "__main__":
    main(sys.argv[1:])
