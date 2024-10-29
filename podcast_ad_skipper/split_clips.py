import json
import os

import librosa
import librosa.display
import numpy as np
from pydub import AudioSegment
from scipy.ndimage import zoom

from podcast_ad_skipper.google_cloud import upload_clips_gcs

# ----------------- Function to split the audio files ----------------- #

def split_files(original_file, ad_list, podcast_name, output_directory, run_env="local"):

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


    is_ad = '0'
    return 'finished'


if __name__ == '__main__':
    #Running the function with podcasts and creating a separate folder for each podcast
    base_directory = 'raw_data/new_podcast_99' # Add the full audio file here
    output_directory = 'raw_data/5_sec_clips/99percentinvisible' # Temporally store for the 5 sec clips -> Google Cloud
    # # Directory where you want to save all podcasts (This need to change for every person)

    # List of audio files with their ad times and podcast names for mp3/wav files:
    # 1: Audio name file with the extation
    # 2: Period in seconds where the ad starts and ends
    # 3: Output name: name podcast and episode

    podcast_files_mp3_wav = [
        # (os.path.join(base_directory, "Glucose Goddess -  The Scary New Research On Sugar!.mp3"), [((60*60)+(16*60+30)), ((60*60)+(18*60+25)), ((60*60)+(38*60+20)), ((60*60)+(39*60+15))], "glucosegoddess"),
        # (os.path.join(base_directory, "Gabrielle Lyon - The Anti-Obesity Doctor,  If You Don't Exercise .mp3"), [60+35, 2*60+5, ((60*60)+(20*60+30)), ((60*60)+(22*60+25)), ((60*60)+(52*60+40)), ((60*60)+(53*60+35))], "gabriellelyon"),
        # (os.path.join(base_directory, "Eye Doctor - They’re Lying To You About Blue Light.mp3"), [((60*60)+(18*60+25)), ((60*60)+(20*60+15)), ((60*60)+(39*60+50)), ((60*60)+(40*60+55))], "eyedoctor"),
        # (os.path.join(base_directory, "Ramit Sethi - Never Split The Bill, It's A Red Flag & Renting Isn't Wasting Money.mp3"),	[((60*60)+(38*60+35)), ((60*60)+(40*60+20)), ((60*60)+(48*60+15)), ((60*60)+(49*60+10))], "ramitsethi"),
        # (os.path.join(base_directory, "Trevor Noah - My Depression Was Linked To ADHD.mp3"), [((120*60)+(17*60)), ((120*60)+(18*60+55)), ((60*60)+(48*60+15)), ((60*60)+(49*60+10))], "trevornoah"),
        # (os.path.join(base_directory, "Boris Johnson - They Were Looking at Engineering The Virus.mp3"), [((60*60)+(12*60+40)), ((60*60)+(14*60+40)), ((60*60)+(51*60+50)), ((60*60)+(52*60+45))], "borisjohnson"),
        (os.path.join(base_directory, "spirithalloween.mp3"), [0,30, ((22*60)+51), ((23*60)+53),((33*60)+49), ((34*60)+50)], "spirit_halloween"),

    ]

    # Loop through each file and process mp3:
    for file_name, ad_list, podcast_name in podcast_files_mp3_wav:
        result = split_files(file_name, ad_list, podcast_name, output_directory)
        print(f'Processing {podcast_name}: {result}')
