from google.cloud import storage
import os
from dotenv import load_dotenv

load_dotenv()

BUCKET_NAME  = os.environ.get('BUCKET_NAME')


def download_all_files(BUCKET_NAME, destination_folder):

    # Initialize the GCS client
    # storage_client = storage.Client()

    # Get the bucket
    # bucket = storage_client.get_bucket(BUCKET_NAME)

    # Ensure the destination folder exists
    # if not {podcast}_OUTPUT_BUCKET_NAME:
    #     os.makedirs({podcast}_OUTPUT_BUCKET_NAME)


















    # Download each file
    for blob in blobs:
        # Create full local path
        destination_path = os.path.join(destination_folder, blob.name)

        # Ensure the local directory exists for nested files
        os.makedirs(os.path.dirname(destination_path), exist_ok=True)

        # Download the file
        blob.download_to_filename(destination_path)

        print(f"Downloaded {blob.name} to {destination_path}")

# Usage example
bucket_name = "your-gcs-bucket-name"
destination_folder = "local/folder/path"  # Local folder to save all files

download_all_files(bucket_name, destination_folder)
