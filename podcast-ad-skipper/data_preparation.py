import numpy as np
import pandas as pd
import os
import time
import librosa
import librosa.display
import matplotlib.pyplot as plt
from pydub import AudioSegment
from scipy.ndimage import zoom

# Function to create a spectrogram from an audio file
def create_spectrogram(audio_file_wav, sr=16000):
    """
    This function takes 1 input to convert wav files to spectrograms:
    """

    #data: is an array representing the amplitude of the audio signal at each sample.
    #sample_rate: is the sampling rate (samples per second)
    data, sample_rate = librosa.load(audio_file_wav, sr=sr) # sr=None to keep the original sample rate (we can change this if needed)
    spectrogram = librosa.feature.melspectrogram(
        y=data,
        sr=sr,
        n_mels=128,  # Number of mel bands
        fmax=8000    # Maximum frequency
    )
    # Short-time Fourier transform
    spectrogram_db = np.array(librosa.power_to_db(mel_spect, ref=np.max))  # Convert to decibel scale
    return spectrogram_db

# -------------------------------------------------------------------------------------------------

def resize_spectrogram(spectrogram, output_size):
    sp_row, sp_col = spectrogram.shape
    out_row, out_col = output_size
    resized_spec = zoom(spectrogram, (out_row/sp_row, out_col/sp_col))
    return resized_spec

# -------------------------------------------------------------------------------------------------

# Function to loop through all clip files and generate spectrograms
def get_features_model (folder_path):
    """
    This function takes 1 input to convert each spectrogram into a list of np.array():
    From this fuction we will get the following:
    spectrograms: This will store the spectrograms of each clip
    labels: This will store the labels of each clip
    seconds: Number of seconds to consider for each clip
    durations: Duration of the full audio file
    podcast_names: This will store the podcast names of each clip
    """
    spectrograms = [] # This will store the spectrograms of each clip
    labels = []  # This will store the labels of each clip
    seconds = []  # Number of seconds to consider for each clip
    durations = []  # Duration of the full audio file
    podcast_names = []  # This will store the podcast names of each clip

    # Iterate over all files in the directory
    file_list = os.listdir(folder_path)
    print(f"Processing files: total {len(file_list)}")
    for filename in file_list:
        # Check if the file is a .wav or .mp3 (you can adjust this as needed)
        if filename.endswith('.wav') or filename.endswith('.mp3'):
            file_path = os.path.join(folder_path, filename)

            # Split the filename by underscore
            filename_parts = filename.split('_')

            # Extract 0 or 1 from the first part of the filename (label: ad or no_ad)
            is_ad = int(filename_parts[0])  # First part is the label

            # Extract the start time in seconds (second part of the filename)
            start_time = int(filename_parts[1])  # Second part is the start time in seconds

            # Extract the total duration (third part of the filename)
            duration = int(filename_parts[2])  # Third part is the total duration of the podcast

             # Extract the podcast name (four part of the filename)
            podcast_name = filename_parts[3].replace('.wav', '')  # Third part is the total duration of the podcast

            # Create spectrogram and convert to numpy array
            spectrogram = create_spectrogram(file_path)
            resized_spectrogram =resize_spectrogram(spectrogram, (96,64))

            # Append the numpy array to the list
            spectrograms.append(resized_spectrogram)
            labels.append(is_ad)
            seconds.append(start_time)
            durations.append(duration)
            podcast_names.append(podcast_name)

    return spectrograms, labels, seconds, durations, podcast_names


# Data folder path: Change this to the path where your audio clips are stored
folder_path = '../raw_data/5_sec_clips/drewbarrymoreasksaboutboogers' # Change this to the path where your audio clips are stored in the Google Colab environment
all_spectrograms = get_features_model(folder_path) # Get the spectrograms and labels - THIS IS THE OUTPUT FOR OUR MODEL AND WE NEED TO ADD IR TO BIG QUERY !!

# Output the number of spectrograms processed
print(f"Processed {len(all_spectrograms[0])} spectrograms.")

# WE CAN USE
# You can use : "make get_fuatures_model" to run this code
