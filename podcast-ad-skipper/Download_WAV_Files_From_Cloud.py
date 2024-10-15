from google.cloud import storage
import os
from dotenv import load_dotenv
import json
import sys
from essay_code_II import create_spectrogram, spectrogram_to_numpy, process_mp3_file
import pandas as pd


from google.auth.exceptions import GoogleAuthError
from google.cloud import storage
from google.oauth2 import service_account
from google.cloud import bigquery


BUCKET_NAME  = os.environ.get('BUCKET_NAME')
GCP_PROJECT_ID= os.environ.get('GCP_PROJECT_ID')
BQ_DATASET= os.environ.get('BQ_DATASET')
BQ_TABLE= os.environ.get('BQ_TABLE')


def call_storage_client():
    """Authenticates and returns a Google Cloud Storage client using service account credentials"""
    try:
        with open('gcp/podcast-ad-skipper-0dd8dd2c5ac1.json') as source:
            info = json.load(source)

        storage_credentials = service_account.Credentials.from_service_account_info(info)

        storage_client = storage.Client(project=os.environ.get('GCP_PROJECT_ID'), credentials=storage_credentials)

        print("Authenticated successfully! ✅")
        return storage_client

    except FileNotFoundError:
        print("Error: The specified credentials file 'gcp/file_name.json' was not found.")
        print("Failed to authenticate with Google Cloud Storage ❌", "red")
        sys.exit(1)

    except GoogleAuthError as e:
        print(f"Error: Authentication failed with Google Cloud: {e}")
        print("Failed to authenticate with Google Cloud Storage ❌", "red")
        sys.exit(1)

    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        print("Failed to authenticate with Google Cloud Storage ❌", "red")
        sys.exit(1)


storage_client = call_storage_client()



def process_audio_file(BUCKET_NAME, blob_name):
    bucket = storage_client.bucket(BUCKET_NAME)
    blob = bucket.blob(blob_name)

    audio_file = blob.open(filename??, 'rb')

    spectrogram_db = create_spectrogram(audio_file)
    spectrogram_to_numpy(spectrogram_db)










def call_bq_client():
    """Authenticates and returns a Google Cloud BigQuery client using service account credentials"""
    try:
        with open('gcp/podcast-ad-skipper-0dd8dd2c5ac1.json') as source:
            info = json.load(source)

        bq_credentials = service_account.Credentials.from_service_account_info(info)

        bq_client = bigquery.Client(project=GCP_PROJECT_ID, credentials=bq_credentials)
        print("Authenticated successfully with BigQuery! ✅")

        return bq_client

    except FileNotFoundError:
        print("Error: The specified credentials file 'gcp/file_name.json' was not found.")
        print("Failed to authenticate with Google Cloud Storage ❌", "red")
        sys.exit(1)

    except GoogleAuthError as e:
        print(f"Error: Authentication failed with Google Cloud: {e}")
        print("Failed to authenticate with Google Cloud Storage ❌", "red")
        sys.exit(1)

    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        print("Failed to authenticate with Google Cloud Storage ❌", "red")
        sys.exit(1)


bq_client = call_bq_client()


table_id = f"{GCP_PROJECT_ID}.{BQ_DATASET}.{BQ_TABLE}"


def append_arrays_to_bq(np_array, table_id):

    # Create df out of the np arrays, to upload to bq
    columns = [f'col_{i}' for i in range(np_array.shape[1])]
    df = pd.DataFrame(np_array, columns=columns)

    # Use WRITE_APPEND to add to the existing table
    job_config = bigquery.LoadJobConfig(write_disposition="WRITE_APPEND")

    job = bq_client.load_table_from_dataframe(df, table_id, job_config=job_config)

    result = job.result()

    print(f"Appended rows to {table_id}")



def process_all_audio_files(BUCKET_NAME, table_id):
    bucket = storage_client.bucket(BUCKET_NAME)
    for blob_name in bucket.list_blobs():
        np_array = process_audio_file(BUCKET_NAME, blob_name)
        append_arrays_to_bq(np_array, table_id)
