import os
import sys
from pathlib import Path

import requests
from google.auth.exceptions import GoogleAuthError
from google.cloud import storage
from google.oauth2 import service_account
from termcolor import colored


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
            service_account_path = current_dir.parent / os.environ.get(
                "GOOGLE_CLOUD_SERVICE_ACCOUNT"
            )

            # Load and return the service account credentials
            credentials = service_account.Credentials.from_service_account_file(
                service_account_path
            )

            storage_client = storage.Client(
                project=os.environ.get("GCP_PROJECT_ID"), credentials=credentials
            )

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


def get_bucket_blobs(client, bucket_name, prefix_name=None):
    # TODO
    """A function that returns a list with blob names for a prefixe o all the files whithn the bucket,
    depends on whether the prefix_name is pass as an argment or not"""


def open_file_bytes_gcs(client, bucket_name, blob_name):
    # TDODO
    """A functions that return the open file from GS, given the blob name. Error if the blon doesn't exit"""


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
#     auth_gc_storage
