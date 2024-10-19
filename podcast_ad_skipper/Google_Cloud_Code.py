from google.cloud import storage
import os
import json
import sys
from podcast_ad_skipper.Spectrogram_Conversion import create_spectrogram
from termcolor import colored
import pandas as pd

from google.auth.exceptions import GoogleAuthError
from google.cloud import storage
from google.oauth2 import service_account
from google.cloud import bigquery

from podcast_ad_skipper.params import *



# Authentication for Google Cloud Storage

# add when local a when gcs b
def auth_gc():
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
        print(colored("Failed to authenticate with Google Cloud Storage ❌", "red"))
        sys.exit(1)

    except GoogleAuthError as e:
        print(f"Error: Authentication failed with Google Cloud: {e}")
        print(colored("Failed to authenticate with Google Cloud Storage ❌", "red"))
        sys.exit(1)

    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        print(colored("Failed to authenticate with Google Cloud Storage ❌", "red"))
        sys.exit(1)


# Uploading local wav files to GCS

def upload_clips_gcs(client, bucket_name, filenames, blobname):
    """Upload every file in a list to a bucket, concurrently in a process pool.

    Each blob name is derived from the filename, not including the
    `source_directory` parameter.
    """

    # A list (or other iterable) of filenames to upload.
    # filenames = ["file_1.txt", "file_2.txt"]

    # The directory on your computer that is the root of all of the files in the
    # list of filenames. This string is prepended (with os.path.join()) to each
    # filename to get the full path to the file. Relative paths and absolute
    # paths are both accepted. This string is not included in the name of the
    # uploaded blob; it is only used to find the source files. An empty string
    # means "the current working directory". Note that this parameter allows
    # directory traversal (e.g. "/", "../") and is not intended for unsanitized
    # end user input.
    # source_directory=""

    # The maximum number of processes to use for the operation. The performance
    # impact of this value depends on the use case, but smaller files usually
    # benefit from a higher number of processes. Each additional process occupies
    # some CPU and memory resources until finished. Threads can be used instead
    # of processes by passing `worker_type=transfer_manager.THREAD`.
    # workers=8
    if client is not None:
        bucket = client.bucket(bucket_name)
        d = bucket.blob(blobname)
        d.upload_from_file(filenames, content_type="audio/wav")

    # for name, result in zip(filenames, results):
    # The results list is either `None` or an exception for each filename in
    # the input list, in order.

    # if isinstance(result, Exception):
    #     print("Failed to upload {} due to exception: {}".format(name, result))
    # else:
    #     print("Uploaded {} to {}.".format(name, bucket.name))

# if __name__ == '__main__':
#     auth_gc()




# Retrieving GCS files to use in VM preprocessing

def retrieve_files_in_folder(storage_client,bucket_name, prefixes):
    file_list = []
    bucket = storage_client.bucket(bucket_name)
    file_list_google_object = bucket.list_blobs(prefix=prefixes)
    for file in file_list_google_object:
        file_list.append(file)
    return file_list


def open_gcs_file(file):
    audio_file = file.open('rb')
    return audio_file


def transform_all_files_to_spectrograms(storage_client, bucket_name, prefixes, spectrogram_list):
    file_list = retrieve_files_in_folder(storage_client, bucket_name, prefixes)

    # Use a dash for the folder names e.g. audio_files/
    # The / helps explicitly indicate that you're targeting files inside a folder
    # rather than a blob whose name starts with the same string but exists at the root level.

    for file in file_list[:6]:
        open_file = open_gcs_file(file)
        spectrogram_db = create_spectrogram(open_file)
        spectrogram_list.append(spectrogram_db)




# BigQuery
# Authentication for Google BigQuery

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



# Transforming np arrays to DFs and uploading to BQ

def append_arrays_to_bq(bq_client, np_array, table_id):
    # Create df out of the np arrays, to upload to bq
    columns = [f'col_{i}' for i in range(np_array.shape[1])]
    df = pd.DataFrame(np_array, columns=columns)

    # Use WRITE_APPEND to add to the existing table
    job_config = bigquery.LoadJobConfig(write_disposition="WRITE_APPEND")

    job = bq_client.load_table_from_dataframe(df, table_id, job_config=job_config)

    print(job.result())

    print(f"Appended rows to {table_id}")
