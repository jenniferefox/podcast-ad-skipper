from podcast_ad_skipper.google_cloud import *
from podcast_ad_skipper.model import *
from podcast_ad_skipper.data_preparation import split_files, make_chunks, get_bq_processed_data
import pandas as pd
import json
from podcast_ad_skipper.google_cloud import auth_gc_storage, auth_gc_bigquery
from podcast_ad_skipper.data_preparation import get_features_model
from podcast_ad_skipper.leo_code_change_name import detect_ads, remove_ads_from_podcast

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
def get_processed_training_data(prefixes, table_name, chunk_size):
    '''Transform audio files into spectrogram'''
    file_count = 0

    storage_client = auth_gc_storage()

    bucket_name = BUCKET_NAME

    bq_client = auth_gc_bigquery()

    table_id = f"{GCP_PROJECT_ID}.{BQ_DATASET}.{table_name}"

    file_list = retrieve_files_in_folder(storage_client, bucket_name, prefixes)

    chunks_list = make_chunks(file_list, chunk_size)

    for chunk in chunks_list:
        features = get_features_model(chunk)
        rows_to_insert = [
                {
                    "spectrogram": json.dumps(features[0][i].tolist()),
                    "labels": features[1][i],
                    "seconds": features[2][i],
                    "duration": features[3][i],
                    "podcast_names": features[4][i],
                } for i in range(len(features[0]))
            ]

        insert_data_to_bq(rows_to_insert, bq_client, table_id, chunk_size)
        file_count += chunk_size
        print(f'Number of processed files: {file_count}')

    print('Done!!')


def retrieve_files_from_bigquery(table_id):
    bq_client = auth_gc_bigquery()
    bigquery_object = get_output_query_bigquery(bq_client, table_id, limit=None, columns="*")
    model_input_columns = get_bq_processed_data(bigquery_object)
    return model_input_columns


def change_name_to_processing_new_ads(podcast_file, model, clip_duration=5):
    ad_segments = detect_ads(podcast_file, model, clip_duration)
    clean_podcast = remove_ads_from_podcast(podcast_file, ad_segments)
    return clean_podcast


def train_plot_accuracy(X_train, y_train, X_test, y_test):
    model = build_baseline_model(
        input_shape=(224,224,3),
        freeze_base=True
    )

    history = model.fit(
        X_train,
        y_train,
        batch_size=16,
        epochs=2,
        validation_data=(X_test,y_test)
    )

    return plot_history(history)


if __name__ == "__main__":
    prefixes=GCP_PREFIXES[11:]
    chunk_size=5
    table_name='podcast-ad-skipper'
    for prefix in prefixes:
        print(f'working on {prefix}')
        get_processed_training_data(prefix, table_name, chunk_size)
