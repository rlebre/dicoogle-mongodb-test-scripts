#!/usr/bin/python

import sys, getopt

from pathlib import Path

import pydicom

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


def main(argv):
    output_dir = 'dataset'
    number_of_files = 0

    try:
        opts, args = getopt.getopt(argv,"hg:o:",["ifile=","output="])
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

    if number_of_files > 0:
        generate_dicom_files(output_dir, number_of_files)

if __name__ == "__main__":
   main(sys.argv[1:])