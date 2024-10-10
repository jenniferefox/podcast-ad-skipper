import os
import time
import librosa
import librosa.display
import numpy as np
import matplotlib.pyplot as plt
from pydub import AudioSegment


#Convert mp3 to wav format
def mp3_to_wav(mp3_path, wav_path):
    AudioSegment.from_mp3(mp3_path).export(wav_path, format="wav")


#Create spectrogram from wav file
def create_spectrogram(wav_path):

    #y is an array representing the amplitude of the audio signal at each sample.
    #sr is the sampling rate (samples per second),
    y, sr = librosa.load(wav_path)
    spectrogram = librosa.stft(y)

    #Transforms to decibel scale (logarithmic), which gives more emphasis to amplitude changes in high volumes
    spectrogram_db = librosa.amplitude_to_db(abs(spectrogram))
    return spectrogram_db


def spectrogram_to_numpy(spectrogram):
    return np.array(spectrogram)




def process_mp3_file(mp3_path, output_dir):
    start_time = time.time()

    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)

    # Generate file names
    # Isolates the file name, without its path and extension (i.e. .mp3)
    base_name = os.path.splitext(os.path.basename(mp3_path))[0]
    # Creates the 3 file paths for the 3 outputs of this code
    wav_path = os.path.join(output_dir, f"{base_name}.wav")
    numpy_path = os.path.join(output_dir, f"{base_name}.npy")

    # Convert MP3 to WAV
    mp3_to_wav(mp3_path, wav_path)

    # Create spectrogram
    spectrogram = create_spectrogram(wav_path)

    # Convert spectrogram to NumPy array and save
    np.save(numpy_path, spectrogram_to_numpy(spectrogram))

    # Remove temporary WAV file
    os.remove(wav_path)

    end_time = time.time()
    processing_time = end_time - start_time

    return numpy_path, processing_time



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
