
import json
import sys

import pandas as pd

from google.auth.exceptions import GoogleAuthError
from google.oauth2 import service_account
from google.cloud import bigquery

from podcast_ad_skipper.params import *


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


def append_arrays_to_bq(bq_client, np_array, table_id):
    # Create df out of the np arrays, to upload to bq
    columns = [f'col_{i}' for i in range(np_array.shape[1])]
    df = pd.DataFrame(np_array, columns=columns)

    # Use WRITE_APPEND to add to the existing table
    job_config = bigquery.LoadJobConfig(write_disposition="WRITE_APPEND")

    job = bq_client.load_table_from_dataframe(df, table_id, job_config=job_config)

    print(job.result())

    print(f"Appended rows to {table_id}")
