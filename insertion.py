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


output_dir='dataset'
generate_dicom_files(output_dir=output_dir, number_of_files=5)

dataset_files = [join(output_dir,f) for f in listdir(output_dir) if isfile(join(output_dir, f))]

mongo = MongoClient(MONGO_HOST, MONGO_PORT, username=MONGO_USER, password=MONGO_PASSWORD)
#mongo = MongoClient('localhost', 27017)
db = mongo.DicoogleDatabase
collection = db.DicoogleObjs

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


# post_id = collection.insert_one(ds_json)
deltaT = time.time_ns()
result = collection.insert_many(dicom_files)
deltaT = time.time_ns() - deltaT

print("Inserted %d objects in %.2f milisseconds." % (len(dicom_files), deltaT/1e6))