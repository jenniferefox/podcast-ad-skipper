from podcast_ad_skipper.google_cloud import auth_gc_storage, get_bucket_blobs, open_file_bytes_gcs
from podcast_ad_skipper.params import BUCKET_NAME, PREFIXES_PODCAST_AD_SKIPPER
from podcast_ad_skipper.utils import list_folders_within_bucket
from podcast_ad_skipper.Spectrogram_Conversion import create_spectrogram

def process_audio_to_array(client, bucket_name, prefix_name):
    spectrogram = []
    file_names = []
    audio_files = get_bucket_blobs(client, bucket_name, prefix_name=prefix_name)
    breakpoint()
    ## just for the first 6 file, changes whenver we are happy with the code
    for file in audio_files[:6]:
        spectrogram.append(create_spectrogram(open_file_bytes_gcs(client,bucket_name, file)))
        file_names.append(file)
    return spectrogram, file_names

def clean_list_folder_in_bucket(client, bucket_name):
    """Function that fetch the blob names within a bucket a return a clean list of the unique folders"""
    blob_names = get_bucket_blobs(client, bucket_name)
    return list_folders_within_bucket(blob_names)


if __name__ == "__main__":
    # Define bucket and Client
    bucket_name = BUCKET_NAME
    storage_Cient = auth_gc_storage

    # Print clean list of folders within bucket
    # clean_list_folder_in_bucket(storage_Cient, bucket_name)

    # Get lists containing spectogram and file names
    spectrogram, file_names = process_audio_to_array(storage_Cient, bucket_name, PREFIXES_PODCAST_AD_SKIPPER[0])
