# %%
#Libraries:
import pandas as pd
import numpy as np
import os
import time
import librosa
import librosa.display
from pydub import AudioSegment
from pydub import AudioSegment

# %%
def detect_ads(podcast_file, model, clip_duration=5):
    """
    This function splits the podcast into clips, creates spectrograms, and passes them to the model to detect ads.
    podcast_file: Path to the podcast audio file (mp3)
    model: The trained model for ad detection
    clip_duration: Duration of each clip in seconds (default 5)
    return: List of ad segments (start_time, end_time) in seconds
    """

    # Load the podcast file
    podcast = AudioSegment.from_file(podcast_file) # Load the new podcast file
    podcast_duration = len(podcast) / 1000  # Duration in seconds

    # List to hold the ad segments
    ad_segments = []

    # Process the podcast in chunks of clip_duration seconds
    for i in range(0, int(podcast_duration), clip_duration):
        start_time = i * 1000  # Convert to milliseconds
        end_time = (i + clip_duration) * 1000

        # Extract the clip from the podcast
        clip = podcast[start_time:end_time]

        # Save the clip as a temporary wav file (for librosa to process)
        clip_file = "temp_clip.wav"
        clip.export(clip_file, format="wav")

        # Create a spectrogram for the clip
        spectrogram = create_spectrogram(clip_file) # We already have this function
        resized_spectrogram =resize_spectrogram(spectrogram, (224,224))
        scaled_spectrogram = minmax_scaler(resized_spectrogram)
        reshaped_spectrogram = reshape_spectrogram(scaled_spectrogram)

        # Convert the spectrogram to a numpy array and pass it to the model
        spectrogram_np = np.expand_dims(reshaped_spectrogram, axis=0)  # Add batch dimension
        prediction = model.predict(spectrogram_np) # Use the model to predict

        # If the model predicts 'ad' it will mark this segment as an ad (1)
        if prediction == 1:
            ad_segments.append((i, i + clip_duration))

        # Clean up the temporary file
        os.remove(clip_file)

    return ad_segments

# # Spectrogram creation function (we already have this)
# def create_spectrogram(audio_file_wav):
#     data, sample_rate = librosa.load(audio_file_wav, sr=None)
#     spectrogram = librosa.stft(data)
#     spectrogram_db = librosa.amplitude_to_db(abs(spectrogram))
#     return spectrogram_db

# %%
def remove_ads_from_podcast(podcast_file, ad_segments):
    """
    Removes the ad segments from the podcast and returns an ad-free podcast.
    podcast_file: Path to the podcast audio file
    ad_segments: List of tuples with (start_time, end_time) of ads in seconds
    return: An AudioSegment object, the podcast without ads
    """
    podcast = AudioSegment.from_file(podcast_file) # Load the podcast file
    podcast_duration = len(podcast)

    clean_podcast = AudioSegment.empty() # Create an empty AudioSegment object
    current_time = 0

    for ad_start, ad_end in ad_segments:
        ad_start_ms = ad_start * 1000 # Convert to milliseconds
        ad_end_ms = ad_end * 1000

        clean_podcast += podcast[current_time:ad_start_ms] # Add the non-ad segment to the clean podcast
        current_time = ad_end_ms  # Update the current time

    clean_podcast += podcast[current_time:podcast_duration]  # Add the last segment of the podcast

    return clean_podcast

# %%
# Example of using the functions:
# podcast_file = "../raw_data/new_podcast_ceo/Boris Johnson - They Were Looking at Engineering The Virus.mp3" # Path to the new podcast file
# ad_segments = detect_ads(podcast_file, model)  # Use trained model here
# clean_podcast = remove_ads_from_podcast(podcast_file, ad_segments)

# # Saving the ad-free podcast:
# clean_podcast.export('podcast_without_ads.mp3', format='mp3')

# # %%
# model.save('model.h5')


# %%
