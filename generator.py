#!/usr/bin/python

import getopt
import json
import os
import sys
from pathlib import Path

from dicomgenerator.exporter import export
from dicomgenerator.factory import CTDatasetFactory
from pydicom._dicom_dict import DicomDictionary


def generate_dicom_objects(number_of_objects):
    """Generates a list of ``number_of_objects`` size containing DICOM objects

    :param number_of_objects: Number of DICOM objects to generate
    :type number_of_objects: int
    :return: A list of DICOM objects
    :rtype: list
    """

    if number_of_objects <= 0:
        return []

    print('\nGenerating DICOM objects...')

    dcm_objects_list = []
    for idx in range(number_of_objects):
        dcm_obj = CTDatasetFactory()
        dcm_objects_list.append(dcm_obj)
        print('{:2.2%} - {}/{}'.format((idx / number_of_objects), idx, number_of_objects), sep=" ", end="\r",
              flush=True)

    print('Finished.\n')

    return dcm_objects_list


def generate_json_objects(number_of_objects):
    """Generates a list of ``number_of_objects`` size containing DICOM objects in JSON format

    :param number_of_objects: Number of DICOM objects to generate
    :type number_of_objects: int
    :return: A list of DICOM objects in JSON format
    :rtype: list
    """

    if number_of_objects <= 0:
        return []

    print('\nGenerating DICOM objects in JSON...')

    dicom_objects_list = []

    for idx in range(number_of_objects):
        dcm_obj = CTDatasetFactory()
        del dcm_obj.PixelData
        ds_json = dcm_obj.to_json_dict()

        new_ds_json = {}
        for key in ds_json.keys():
            try:
                if ds_json[key].get("Value") is not None:
                    new_ds_json[DicomDictionary[int(key, 16)][4]] = (
                        ds_json[key]["Value"][0] if len(ds_json[key]["Value"]) == 1 else ds_json[key]["Value"])
            except:
                pass

        dicom_objects_list.append(new_ds_json)

        print('{:2.2%} - {}/{}'.format((idx / number_of_objects), idx, number_of_objects), sep=" ", end="\r",
              flush=True)

    print('Finished.\n')

    return dicom_objects_list


def generate_dicom_files(output_path, number_of_files):
    """Generates ``number_of_objects`` DICOM files in the directory provided

    :param number_of_files: Number of DICOM files to generate
    :type number_of_files: int
    :param output_path: Path where the files will be stored
    :type output_path: Path
    """

    filenames = [f"dcmfile_{x + 1}.dcm" for x in range(number_of_files)]

    print('\nGenerating DICOM files...')

    for idx, filename in enumerate(filenames):
        export(dataset=CTDatasetFactory(), path=output_path / filename)

        print('{:2.2%} - {}/{}'.format((idx / len(filenames)), idx, len(filenames)), sep=" ", end="\r", flush=True)

    print('Finished generating DICOM files.\n')


def generate_json_files(output_path, number_of_files):
    """Generates ``number_of_objects`` DICOM files in JSON format in the directory provided

    :param number_of_files: Number of DICOM files in JSON format to generate
    :type number_of_files: int
    :param output_path: Path where the files will be stored
    :type output_path: Path
    """

    filenames = [f"dcmfile_{x + 1}.json" for x in range(number_of_files)]

    print('\nGenerating DICOM files in JSON format...')

    for idx, filename in enumerate(filenames):
        dataset = CTDatasetFactory()
        del dataset.PixelData
        ds_json = dataset.to_json_dict()

        new_ds_json = {}
        for key in ds_json.keys():
            try:
                if ds_json[key].get("Value") is not None:
                    new_ds_json[DicomDictionary[int(key, 16)][4]] = (
                        ds_json[key]["Value"][0] if len(ds_json[key]["Value"]) == 1 else ds_json[key]["Value"])
            except:
                pass

        with open(output_path / filename, 'w') as outfile:
            json.dump(new_ds_json, outfile)

        print('{:2.2%} - {}/{}'.format((idx / len(filenames)), idx, len(filenames)), sep=" ", end="\r", flush=True)

    print('Finished generating DICOM files in JSON format.\n')


def main(argv):
    """Main function that parses the input arguments

    :param argv: List of arguments
    :type argv: list
    """
    
    usage = 'generator.py -n <number_to_generate> -o <output_directory> -d|-d <dicom_format | json_format'
    output_dir = ''
    output_path = Path(output_dir)
    number_of_files = 0
    generate_in_dicom = True

    try:
        opts, args = getopt.getopt(argv, "hn:o:djf", ["number=", "output=", "dicom=", "json="])
    except getopt.GetoptError:
        print(usage)
        sys.exit(1)

    for opt, arg in opts:
        if opt == '-h':
            print(usage)
            sys.exit()
        elif opt in ("-n", "--number"):
            try:
                number_of_files = int(arg)
            except ValueError:
                sys.exit("-n | --number argument must be integer. Program will not run.")
        elif opt in ("-o", "--output"):
            try:
                output_dir = arg
                output_path = Path(output_dir)
                output_path.mkdir(parents=True, exist_ok=True)
            except:
                sys.exit("Error creating/accessing output directory. Program will not run.")
        elif opt in ("-j", "--json"):
            generate_in_dicom = False
        elif opt in ("-d", "--dicom"):
            generate_in_dicom = True

    if number_of_files <= 0:
        sys.exit("You must define a positive number of files/objects to generate. Program will not run.")

    if output_dir == "":
        sys.exit("You must provide the output directory. Program will not run.")

    if not os.access(output_dir, os.W_OK):
        sys.exit("You do not have writing permissions on output directory. Program will not run.")

    if generate_in_dicom:
        generate_dicom_files(output_path, number_of_files)
    else:
        generate_json_files(output_path, number_of_files)


if __name__ == "__main__":
    main(sys.argv[1:])
