#!/usr/bin/python

import sys, getopt

from pathlib import Path

import pydicom
from pydicom._dicom_dict import DicomDictionary as dcm_dict
import json

from dicomgenerator.exporter import export
from dicomgenerator.factory import CTDatasetFactory


def generate_dicom_files(output_dir = './dataset', number_of_files=5):
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    filenames = [f"dcmfile{x}" for x in range(number_of_files)]

    print('\nGenerating DICOM files...')
    
    for idx, filename in enumerate(filenames):
        export(dataset=CTDatasetFactory(), path=output_path / filename)

        print('{:2.2%} - {}/{}'.format((idx / len(filenames)), idx, len(filenames)), sep=" ", end="\r", flush=True)

    print('Finished generating DICOM files.\n')

def generate_dicom_to_json(output_dir = './dataset', number_of_files=5):
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    filenames = [f"dcmfile{x}" for x in range(number_of_files)]

    print('\nGenerating DICOM files...')
    
    for idx, filename in enumerate(filenames):
        dataset = CTDatasetFactory()
        del dataset.PixelData
        ds_json = dataset.to_json_dict()
        
        new_ds_json = {}
        for key in ds_json.keys():
            try:
                if ds_json[key].get("Value") is not None:
                    a = dcm_dict[int(key, 16)][4]
                    b= ds_json[key]["Value"][0]
                    c= len(ds_json[key]["Value"])
                    d= ds_json[key]["Value"]
                    new_ds_json[dcm_dict[int(key, 16)][4]] = (ds_json[key]["Value"][0] if len(ds_json[key]["Value"]) == 1 else ds_json[key]["Value"])
            except:
                pass

        with open(output_path / filename, 'w') as outfile:
            json.dump(new_ds_json, outfile)


        print('{:2.2%} - {}/{}'.format((idx / len(filenames)), idx, len(filenames)), sep=" ", end="\r", flush=True)

    print('Finished generating DICOM files in JSON format.\n')

def main(argv):
    output_dir = 'dataset'
    number_of_files = 0
    generate_in_dicom = True

    try:
        opts, args = getopt.getopt(argv,"hg:o:j:",["ifile=","output="])
    except getopt.GetoptError:
        print('generator.py -i <number of DICOM files to generate> -o <output_directory>')
        sys.exit(2)

    for opt, arg in opts:
        if opt == '-h':
            print('generator.py -g <number of DICOM files to generate> -o <output_directory>')
            sys.exit()
        elif opt in ("-g", "--generate"):
            try:
                number_of_files = int(arg)
            except ValueError:
                sys.exit("-g | --generate argument must be integer. Program will not run.")
        elif opt in ("-o", "--output"):
            output_dir = arg
        elif opt in ("-j", "--json"):
            try:
                number_of_files = int(arg)
                generate_in_dicom = False
            except ValueError:
                sys.exit("-j | --json argument must be integer. Program will not run.")
        
    if number_of_files > 0 and generate_in_dicom:
        generate_dicom_files(output_dir, number_of_files)
    elif number_of_files > 0 and not generate_in_dicom:
        generate_dicom_to_json(output_dir, number_of_files)

if __name__ == "__main__":
   main(sys.argv[1:])