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