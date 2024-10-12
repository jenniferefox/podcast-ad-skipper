import json
import os

from google.cloud import storage
from google.oauth2 import service_account


def auth_gc():
    # wip
    with open('gcp/podcast-ad-skipper-0dd8dd2c5ac1.json') as source:
        info = json.load(source)

    storage_credentials = service_account.Credentials.from_service_account_info(info)

    storage_client = storage.Client(project=os.environ.get('GCP_PROJECT_ID'), credentials=storage_credentials)

    return storage_client

def upload_files_to_gcloud(bucket_name, filenames, blobname):
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
    with open('gcp/podcast-ad-skipper-0dd8dd2c5ac1.json') as source:
        info = json.load(source)

    storage_credentials = service_account.Credentials.from_service_account_info(info)

    storage_client = storage.Client(project=os.environ.get('GCP_PROJECT_ID'), credentials=storage_credentials)

    bucket = storage_client.bucket(bucket_name)

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
