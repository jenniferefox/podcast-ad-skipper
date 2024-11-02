import sys
from pathlib import Path

import requests
from google.auth.exceptions import GoogleAuthError
from google.cloud import bigquery, storage
from google.oauth2 import service_account
from termcolor import colored

from podcast_ad_skipper.params import *


def auth_gc_storage():
    """Authenticates and returns a Google Cloud Storage client using service account credentials"""

    # Check if running in a Google Cloud environment (e.g., a VM or Cloud Function)
    try:
        # The metadata server is only available on Google Cloud environments
        response = requests.get("http://metadata.google.internal", timeout=1)
        if response.status_code == 200:
            # Running in Google Cloud, no need to specify credentials
            print("Running in Google Cloud environment.")
            print("Authenticated successfully! ✅")
            return storage.Client()

    except (requests.exceptions.RequestException, ValueError):
        # Running locally, load credentials from a file
        print("Running in local environment.")
        try:
            current_dir = Path(__file__).parent

            # Define the path to the service account folder (relative to the main project root)
            service_account_path = current_dir.parent / GOOGLE_CLOUD_SERVICE_ACCOUNT

            # Load and return the service account credentials
            credentials = service_account.Credentials.from_service_account_file(
                service_account_path
            )

            storage_client = storage.Client(
                project=GCP_PROJECT_ID, credentials=credentials
            )

            print("Authenticated successfully with GCS! ✅")
            return storage_client

        except FileNotFoundError:
            print(
                "Error: The specified credentials file 'gcp/file_name.json' was not found."
            )
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


def upload_clips_gcs(client, bucket_name, filenames, blobname):
    """Upload every file in a list to a bucket, concurrently in a process pool.

    Each blob name is derived from the filename, not including the
    `source_directory` parameter.
    """
    if client is not None:
        bucket = client.bucket(bucket_name)
        d = bucket.blob(blobname)
        d.upload_from_file(filenames, content_type="audio/wav")

    if d.exists():
        print("Uploaded {blobname} to {bucket_name}")
    else:
        print("Failed to upload {blobname} to {bucket_name}")


def retrieve_files_in_folder(storage_client, bucket_name, prefixes):
    """Retrieving GCS files to use in VM preprocessing"""
    file_list = []
    bucket = storage_client.bucket(bucket_name)
    file_list_google_object = bucket.list_blobs(prefix=prefixes)
    for file in file_list_google_object:
        file_list.append(file)
    return file_list


def open_gcs_file(file):
    """Open audio file from GCS"""
    audio_file = file.open("rb")
    return audio_file


def auth_gc_bigquery():
    """Authenticates and returns a Google Cloud BigQuery client using service account credentials"""
    try:
        # The metadata server is only available on Google Cloud environments
        response = requests.get("http://metadata.google.internal", timeout=1)
        if response.status_code == 200:
            # Running in Google Cloud, no need to specify credentials
            print("Running in Google Cloud environment.")
            print("Authenticated successfully! ✅")
            return bigquery.Client()

    except (requests.exceptions.RequestException, ValueError):
        # Running locally, load credentials from a file
        print("Running in local environment.")
        try:
            current_dir = Path(__file__).parent

            # Define the path to the service account folder (relative to the main project root)
            service_account_path = current_dir.parent / GOOGLE_CLOUD_SERVICE_ACCOUNT

            # Load and return the service account credentials
            bq_credentials = service_account.Credentials.from_service_account_file(
                service_account_path
            )

            bq_client = bigquery.Client(project=GCP_PROJECT_ID, credentials=bq_credentials)
            print("Authenticated successfully with BigQuery! ✅")

            return bq_client

        except FileNotFoundError:
            print(
                "Error: The specified credentials file 'gcp/file_name.json' was not found."
            )
            print("Failed to authenticate with Big Query ❌", "red")
            sys.exit(1)

        except GoogleAuthError as e:
            print(f"Error: Authentication failed with Google Cloud: {e}")
            print("Failed to authenticate with Big Query ❌", "red")
            sys.exit(1)

        except Exception as e:
            print(f"An unexpected error occurred: {e}")
            print("Failed to authenticate with Big Query ❌", "red")
            sys.exit(1)


def insert_data_to_bq(rows_to_insert, bq_client, table_id, data_chunks):
    """Uploading data into BQ using json in batches of specified size (default: 5)."""

    errors = bq_client.insert_rows_json(table=table_id, json_rows=rows_to_insert)

    if errors == []:
        print(f"Batch of {data_chunks} rows has been added.")
    else:
        print(f"Encountered errors while inserting rows: {errors}")


def get_output_query_bigquery(bq_client, table_id, custom=None, limit=None, columns="*"):
    """Given a string with columns and an table id, this function returns the result of
    the query with necessary columns. Also, give the option to limit the number of records to output
    """
    try:
        # Define the query: WE NEED TO CHANGE THIS TO A CUSTOM QUERY AND THE LIMIT TO A CUSTOM LIMIT
        if custom is not None:
            query = f"""
            WITH ads AS (
            SELECT spectrogram, labels
            FROM `podcast-ad-skipper.Numpy_Arrays_Dataset.processed_train_data_II`
            WHERE labels = 1
            ),
            no_ads AS (
                SELECT spectrogram, labels
                FROM `podcast-ad-skipper.Numpy_Arrays_Dataset.processed_train_data_II`
                WHERE labels = 0
                AND MOD(FARM_FINGERPRINT(CAST(spectrogram AS STRING)), 100) < 1  -- Adjust percentage if needed
                LIMIT 2934
            )

            SELECT * FROM ads
            UNION ALL
            SELECT * FROM no_ads

                    """
        elif limit is None:
            query = f"""SELECT {columns}
                        from {table_id}"""
        else:
            query = f"""SELECT {columns}
                    from {table_id}
                    limit {limit}"""

        # Run the query
        query_job = bq_client.query(query)

        results = query_job.result()

        if results.total_rows == 0:
            print(colored("Query returned no results", "yellow"))
            return None
        else:
            print(colored(f"Query returned {results.total_rows} results", "green"))
            return results

    except Exception as e:
        print(colored(f"An error occurred: {e}", "red"))


def count_files_in_gcs(prefixes):
    '''Transform audio files into spectrogram'''

    storage_client = auth_gc_storage()
    bucket_name = BUCKET_NAME

    for prefix in prefixes:

        count = 0
        file_list = []

        bucket = storage_client.bucket(bucket_name)

        file_list_google_object = bucket.list_blobs(prefix=prefix)

        for file in file_list_google_object:
            file_list.append(file)
            count += 1

        print(f'{prefix}: {count}')




if __name__ == "__main__":
    auth_gc_storage()
    auth_gc_bigquery()
