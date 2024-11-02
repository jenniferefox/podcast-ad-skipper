import json
import os

import librosa
import librosa.display
import numpy as np
from pydub import AudioSegment
from scipy.ndimage import zoom

from podcast_ad_skipper.google_cloud import *
from podcast_ad_skipper.params import *

CORRECT_SPECTROGRAM_SHAPE = (128, 216)
# ----------------- Function to split the audio files ----------------- #

def split_files(original_file, ad_list, podcast_name, output_directory, google_client, run_env="gc"):

    """
    This function takes an original audio file name, list of integers showing
    when each ad starts and ends and a podcast name and splits up the original
    file into 5 second chunks, naming each one according to whether it contains
    ads or not.
    """

    # Create a folder for the podcast and their clips:
    podcast_folder = os.path.join(output_directory, podcast_name)

    if run_env == "local":
        #Check if the folder already exists and has any .mp3 files
        if os.path.exists(podcast_folder) and any(fname.endswith('.wav') for fname in os.listdir(podcast_folder)):
            print(f"Skipping {podcast_name} because it has already been processed.")
            return 'skipped'

        # Create the directory if doesnt exist:
        if not os.path.exists(podcast_name):
            os.makedirs(podcast_folder)
            print(f"Created folder: {podcast_folder}")


    # Determine the file extension and load the audio file accordingly
    file_extension = os.path.splitext(original_file)[1].lower()

    if file_extension == '.mp3':
        new_audio = AudioSegment.from_mp3(original_file)
    elif file_extension == '.wav':
        new_audio = AudioSegment.from_wav(original_file)
    else:
        raise ValueError(f"Unsupported file format: {file_extension}. Only .mp3 and .wav are supported.")

    # Save duration
    duration = int(new_audio.duration_seconds)

    # Set default to no_ad
    is_ad = '0'

    # If the ad_list doesn't start with 0, then the ads don't start straight away.
    # in this case, insert '0' first in the list so that a segment is created at the start.
    if ad_list[0] != 0:
        ad_list.insert(0, 0)
        is_ad = '1'

    # Add duration at the end so that the end segments can be made.
    if ad_list[-1] != duration:
        ad_list.append(duration)

    #Go through each segement in the list, label whether the section is an ad or not
    for index in range(0,len(ad_list)-1):
        start = ad_list[index]
        end = ad_list[index+1]
        # Toggle between 'ad' and 'no_ad'
        if is_ad == '1':
            is_ad = '0'
        else:
            is_ad = '1'

        # Go through each second in the segment and create a new 5 second clip from here.
        # Stop before the end of the segment so that only 5 second clips are created
        for tc in range(start, (end-4)):
            start_clip = tc*1000 #pydub works with milliseconds, so seconds are converted here
            end_clip = (tc+5)*1000

            # Construct the file path for saving
            output_file = os.path.join(podcast_folder, f'{is_ad}_{tc}_{duration}_{podcast_name}.wav')

            if run_env == "local":
                # Save clip locally:
                new_audio[start_clip:end_clip].export(output_file, format='wav')
                print(f"Saved clip: {output_file}")

            elif run_env == "gc":
                 # Save clip in Google Cloud Storage:
                new_clip = new_audio[start_clip:end_clip].export(format='wav')
                upload_clips_gcs(google_client, BUCKET_NAME, new_clip, f'{podcast_name}/{is_ad}_{tc}_{duration}_{podcast_name}.wav')
                print(f"Saved clip in Google Cloud Storage: {is_ad}_{tc}_{duration}_{podcast_name}.wav")

    is_ad = '0'
    return 'finished'

# ----------------- Functions to convert audio clips to spectrograms ----------------- #

def make_chunks(file_list, chunk_size):
    """Split the data into chunks of a specified size."""
    data_chunks = []
    for i in range(0, len(file_list), chunk_size):
        data_chunks.append(file_list[i:i + chunk_size])
    return data_chunks


def create_spectrogram(audio_file_wav, sr=22050):
    """
    Converts wav files to spectrograms.
    sr=None to keep the original sample rate
    """

    #data: is an array representing the amplitude of the audio signal at each sample.
    #sample_rate: is the sampling rate (samples per second)
    data, sample_rate = librosa.load(audio_file_wav, sr=sr)
    spectrogram = librosa.feature.melspectrogram(
        y=data,
        sr=sample_rate,
        n_mels=128,  # Number of mel bands
        fmax=8000    # Maximum frequency
    )
    # Convert to log scale and return
    return np.array(librosa.power_to_db(spectrogram, ref=np.max))

# ----------------- Functions to get the features for the model ----------------- #

def get_features_model(clip_audio_files, run_env="gc"):
    """
    Creates spectrograms and converts into np arrays.
    """
    spectrograms = [] # This will store the spectrograms of each clip
    labels = []  # This will store the labels of each clip
    seconds = []  # Number of seconds to consider for each clip
    durations = []  # Duration of the full audio file
    podcast_names = []  # This will store the podcast names of each clip

    # Iterate over all files in the directory
    if run_env == "local":
        file_list = os.listdir(clip_audio_files)
    elif run_env == 'gc':
        file_list = clip_audio_files

    for filename in file_list:
        # Split the filename by underscore
        if run_env == "local":
            filename_parts = filename.split('_')
        elif run_env == 'gc':
            filename_parts = filename.name.split('/')[1].split('_')


        # Extract 0 or 1 from the first part of the filename (label: ad or no_ad)
        is_ad = int(filename_parts[0])  # First part is the label
        # Extract the start time in seconds (second part of the filename)
        start_time = int(filename_parts[1])  # Second part is the start time in seconds
        # Extract the total duration (third part of the filename)
        duration = int(filename_parts[2])  # Third part is the total duration of the podcast
         # Extract the podcast name (four part of the filename)
        podcast_name = filename_parts[3].replace('.wav', '')  # Third part is the total duration of the podcast

        if run_env == "local":
            file_path = os.path.join(clip_audio_files, filename)
        elif run_env == 'gc':
            file_path = filename.open('rb')

        spectrogram = create_spectrogram(file_path)

        if spectrogram.shape == CORRECT_SPECTROGRAM_SHAPE:

            # Append the numpy array to the list
            spectrograms.append(spectrogram)
            labels.append(is_ad)
            seconds.append(start_time)
            durations.append(duration)
            podcast_names.append(podcast_name)

        else:
            print(f'{filename_parts} is not correct shape. Instead shape is {spectrogram.shape}')

    return spectrograms, labels, seconds, durations, podcast_names

def get_bq_processed_data(output):
    if output:
        spectrogram_bq, labels_bq = [], []
        for row in output:
            # Use row.field_name to access fields instead of indices
            spectrogram_bq.append(np.array(json.loads(row['spectrogram'])))
            labels_bq.append(row['labels'])
        return spectrogram_bq, labels_bq




if __name__ == '__main__':
    base_directory = 'raw_data/new_podcast_ceo' # Add the full audio file here
    output_directory = 'raw_data/5_sec_clips' # Temporally store for the 5 sec clips -> Google Cloud

    podcast_files_mp3_wav = [
        # (os.path.join(base_directory, "Glucose Goddess -  The Scary New Research On Sugar!.mp3"), [((60*60)+(16*60+30)), ((60*60)+(18*60+25)), ((60*60)+(38*60+20)), ((60*60)+(39*60+15))], "glucosegoddess"),
        # (os.path.join(base_directory, "Gabrielle Lyon - The Anti-Obesity Doctor,  If You Don't Exercise .mp3"), [60+35, 2*60+5, ((60*60)+(20*60+30)), ((60*60)+(22*60+25)), ((60*60)+(52*60+40)), ((60*60)+(53*60+35))], "gabriellelyon"),
        # (os.path.join(base_directory, "Eye Doctor - They’re Lying To You About Blue Light.mp3"), [((60*60)+(18*60+25)), ((60*60)+(20*60+15)), ((60*60)+(39*60+50)), ((60*60)+(40*60+55))], "eyedoctor"),
        # (os.path.join(base_directory, "Ramit Sethi - Never Split The Bill, It's A Red Flag & Renting Isn't Wasting Money.mp3"),	[((60*60)+(38*60+35)), ((60*60)+(40*60+20)), ((60*60)+(48*60+15)), ((60*60)+(49*60+10))], "ramitsethi"),
        # (os.path.join(base_directory, "Trevor Noah - My Depression Was Linked To ADHD.mp3"), [((120*60)+(17*60)), ((120*60)+(18*60+55)), ((60*60)+(48*60+15)), ((60*60)+(49*60+10))], "trevornoah"),
        # (os.path.join(base_directory, "Boris Johnson - They Were Looking at Engineering The Virus.mp3"), [((60*60)+(12*60+40)), ((60*60)+(14*60+40)), ((60*60)+(51*60+50)), ((60*60)+(52*60+45))], "borisjohnson"),
    ]


    # authentication with google cloud
    google_client = auth_gc_storage()
    # Loop through each file and process mp3:
    for file_name, ad_list, podcast_name in podcast_files_mp3_wav:
        result = split_files(file_name, ad_list, podcast_name, output_directory, google_client)

        print(f'Processing {podcast_name}: {result}')
