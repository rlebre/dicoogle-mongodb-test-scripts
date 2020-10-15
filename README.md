# Scripts to generate DICOM files and insert them in MongoDB instance

This project is composed by two scripts:

- generator.py: generates CT files in DICOM format
- insert.py: generates CT files in DICOM format and inserts them in a MongoDB endpoint

## Requirements

- Python3
- Installation of requirements.txt

## Instructions

1. Clone this repository

   ```shell script
   git clone https://github.com/rlebre/dicoogle-mongodb-test-scripts.git
   ```

2. Install virtual environment

   ```shell script
   virtualenv -p python3 venv
   ```

3. Activate virtual environment

   ```shell script
   source venv/bin/activate
   ```

4. Install requirements.py

   ```shell script
   pip install -r requirements.txt
   ```

5. Edit your configuration

6. Run `insert.py`

   ```shell script
   python insert.py -g 1000 -o dataset #generates 1000 DICOM files in directory ./dataset
   ```

   Usage: `insert.py -g <number of DICOM files to generate> -o <output_directory>`

7. Or run `generate.py`

   ```shell script
   python generate.py -g 1000 -o dataset #generates 1000 DICOM files in directory ./dataset
   ```

   Usage: `generate.py -g <number of DICOM files to generate> -o <output_directory>`

### Configuration

You must configure your MongoDB instance first and provide the configurations in `local_settings.py`. Example:

```python
MONGO_HOST='localhost'
MONGO_PORT=27017
MONGO_USER='dicoogle'
MONGO_PASSWORD='dicoogle'
```

## Acknowledgments

- Thank you to the contributors of [pydicom](pydicom/pydicom)
- Thank you to Sjoerd for [dicomgenerator](sjoerdk/dicomgenerator)
- Thank you to the contributors of [pymongo](mongodb/mongo-python-driver)

### Disclaimer

This work received support from FCT, Fundação para a Ciência e a Tecnologia, under the project UID/CEC/00127/2019 and POCI-01-0145-FEDER-016385 (NETDIAMOND)
