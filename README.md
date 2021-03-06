# Scripts to generate DICOM files and insert them in MongoDB instance

This project is composed by two scripts:

- generator.py: generates DICOM objects or files (Computed Tomographies)
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

### Insert

6. Run `generator.py` and `insertion.py

   ```shell script
   python generator.py -n 1000 -o ./dataset -j #generates 1000 files in the directory './dataset' 
   python insertion.py -c 50 -j ./dataset # reads database directory and inserts each 50 in database
   ```

   Usage: `generator.py -n <number_to_generate> -o <output_directory> -d|-d <dicom_format | json_format`>


6. Run simply generate objects in runtime `insertion.py`

   ```shell script
   python insertion.py -n 1000 -c 50 # generates 1000 objects and inserts each 50 in database
   ```

   Usage: `insertion.py -n <number_of_objects_to_insert -c <chunk_size> -j/-d <dicom|json_directory>`


### Query

8. Or run `querying.py`

   ```shell script
   python querying.py [-i] [-d] [-q <query>] #generates 1000 DICOM files in directory ./dataset
   ```

   ```
   -i - create indexes
   -d - drop indexes
   -q - query
   ```

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
