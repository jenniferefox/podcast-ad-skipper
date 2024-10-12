from google.cloud import storage
import os
from dotenv import load_dotenv

load_dotenv()

BUCKET_NAME  = os.environ.get("BUCKET_NAME")







def download_all_files(BUCKET_NAME, destination_folder):
    """
    Download all files from a Google Cloud Storage bucket to a local folder.

    :param bucket_name: Name of the GCS bucket
    :param destination_folder: Local folder where the files will be saved
    """
    # Initialize the GCS client
    storage_client = storage.Client()

    # Get the bucket
    bucket = storage_client.get_bucket(bucket_name)

    # List all files in the bucket
    blobs = bucket.list_blobs()

    # Ensure the destination folder exists
    if not os.path.exists(destination_folder):
        os.makedirs(destination_folder)










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
