from podcast_ad_skipper.google_cloud import auth_gc_storage, get_bucket_blobs
from podcast_ad_skipper.params import BUCKET_NAME
from podcast_ad_skipper.utils import list_folders_within_bucket


def clean_list_folder_in_bucket(client, bucket_name):
    """Function that fetch the blob names within a bucket a return a clean list of the unique folders"""
    blob_names = get_bucket_blobs(storage_Cient, BUCKET_NAME)
    return list_folders_within_bucket(blob_names)


if __name__ == "__main__":
    bucket_name = BUCKET_NAME
    storage_Cient = auth_gc_storage
