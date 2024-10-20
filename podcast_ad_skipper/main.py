from podcast_ad_skipper.google_cloud import *
from podcast_ad_skipper.data_preparation import split_files
import pandas as pd
import json

def need_to_change(gcs_client):
    base_directory = 'raw_data/full_podcast' # Add the full audio file here
    output_directory = 'raw_data/5_sec_clips' # Temporally store for the 5 sec clips -> Google Cloud
    # List of audio files with their ad times and podcast names for mp3/wav files:
    # 1: Audio name file with the extation
    # 2: Period in seconds where the ad starts and ends
    # 3: Output name: name podcast and episode

    podcast_files_mp3_wav = [
        (os.path.join(base_directory, "CEO181.mp3"), [0, 44, (9*60)+39, (11*60)+21], "ceo181"),
    ]

    # Loop through each file and process mp3:
    for file_name, ad_list, podcast_name in podcast_files_mp3_wav:
        result = split_files(file_name, ad_list, podcast_name, output_directory, gcs_client)

        print(f'Processing {podcast_name}: {result}')

# Main function, to be updated
def we_need_to_change_name_preprocess_data(prefixes):
    '''Transform audio files into spectrogram'''
    storage_client = auth_gc()
    bucket_name = BUCKET_NAME
    file_list = retrieve_files_in_folder(storage_client, bucket_name, prefixes)

    # Use a dash for the folder names e.g. audio_files/
    # The / helps explicitly indicate that you're targeting files inside a folder
    # rather than a blob whose name starts with the same string but exists at the root level.
    for file in file_list[:6]:
        open_file = open_gcs_file(file)

    rows_to_insert = [
            {
                "spectrogram": json.dumps(features[0][i].tolist()),
                "label": features[1][i],
                "seconds": features[2][i],
                "duration": features[3][i],
                "podcast_name": features[3][i],
            } for i  in range(len(features[0]))
        ]

def serialise_array(array):
    '''Converts the spectrogram's 3D array into a JSON string representation'''
    return json.dumps(array.tolist())


def transform_features_into_dataframe(features):
    data = pd.DataFrame(features).T
    columns = ['spectrogram', 'labels', 'seconds', 'durations', 'podcast_names']
    data.columns = columns
    # Apply the serialise function to the spectrogram column
    data['spectrogram'] = data['spectrogram'].apply(serialise_array)
    return data





if __name__ == "__main__":

    we_need_to_change_name_preprocess_data
