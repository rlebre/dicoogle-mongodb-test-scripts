import pydicom
import time
from pymongo import MongoClient
from generator import generate_dicom_files
from local_settings import *

generate_dicom_files()

mongo = MongoClient(MONGO_HOST, MONGO_PORT, username=MONGO_USER, password=MONGO_PASSWORD)
db = mongo.DicoogleDatabase
collection = db.DicoogleObjs

filename = "2.dcm"
ds = pydicom.dcmread(filename)
del ds.PixelData
ds_json = ds.to_json_dict()

deltaT = time.time_ns()
post_id = collection.insert_one(ds_json)
deltaT = time.time_ns() - deltaT

#result = collection.insert_many(ds_json)

print(deltaT)
