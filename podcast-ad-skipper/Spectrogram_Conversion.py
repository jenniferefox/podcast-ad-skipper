import os
import time
import librosa
import librosa.display
import numpy as np
import matplotlib.pyplot as plt
from pydub import AudioSegment


#Convert mp3 to wav format
# def mp3_to_wav(mp3_path, wav_path):
#     AudioSegment.from_mp3(mp3_path).export(wav_path, format="wav")


#Create spectrogram from wav file
def create_spectrogram(audio_file):
    #y is an array representing the frequency of the audio signal at each sample.
    #sr is the sampling rate (samples per second),
    y, sr = librosa.load(audio_file)
    spectrogram = librosa.stft(y)

    #Transforms to decibel scale (logarithmic), which gives more emphasis to amplitude changes in high volumes
    spectrogram_db = librosa.amplitude_to_db(abs(spectrogram))
    return spectrogram_db


def spectrogram_to_numpy(spectrogram_db):
    return np.array(spectrogram_db)














# FOR LOCAL USE ONLY ----- DO NOT USE ----- JUST FOR INSPO
def process_directory(input_dir, output_dir):

    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)

    total_start_time = time.time()

    # For testing, to print the total no of files processed
    file_count = 0

    # Process all MP3 files in the input directory
    for filename in os.listdir(input_dir):
        if filename.lower().endswith('.mp3'):
            mp3_path = os.path.join(input_dir, filename)
            numpy_path, processing_time = process_mp3_file(mp3_path, output_dir)
            file_count += 1

    total_end_time = time.time()
    total_processing_time = total_end_time - total_start_time

    print(f"Total files processed: {file_count}")
    print(f"Total processing time: {total_processing_time:.2f} seconds")
    print(f"Average processing time per file: {total_processing_time / file_count:.2f} seconds")


# Example usage
input_directory = "/Users/irenegracia/code/jenniferefox/podcast-ad-skipper/raw_data"
output_directory = "/Users/irenegracia/code/jenniferefox/podcast-ad-skipper/raw_data"
process_directory(input_directory, output_directory)
