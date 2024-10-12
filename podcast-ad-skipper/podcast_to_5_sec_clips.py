# Import Libraries:
import os
from pydub import AudioSegment

def split_files(original_file, ad_list, podcast_name, output_directory):

    """
    This function takes 3 inputs to convert mp3 or wav files:
    The audio file that is to be split up
    A list of integers which shows when each ad starts and ends. The list must be an even length to include the in and out time of each ad.
    the name of the podcast, to be used in the final file output name
    IMPORTANT Before running this, make sure that your mp3/wav file is saved in the same folder. You may need to copy this in your raw_data folder
    """

    # Create a folder for the podcast and their clips:
    podcast_folder = os.path.join(output_directory, podcast_name)

    #Check if the folder already exists and has any .mp3 files
    if os.path.exists(podcast_folder) and any(fname.endswith('.wav') for fname in os.listdir(podcast_folder)):
        print(f"Skipping {podcast_name} because it has already been processed.")
        return 'skipped'

    # Create the directory if doesnt ecist:
    if not os.path.exists(podcast_name):
        os.makedirs(podcast_folder)
        print(f"Created folder: {podcast_folder}")

    # Import original_file
    new_audio = AudioSegment.from_mp3(original_file)

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
            print(f"Saving clip: {output_file}")

            # Making a clip files:
            new_audio[start_clip:end_clip].export(output_file, format='wav')

    is_ad = '0'
    return 'finished'


#Running the function with podcasts and creating a separate folder for each podcast
base_directory = 'raw_data/full_podcast' # Add the full audio file here
output_directory = 'raw_data/5_sec_clips' # Temporally store for the 5 sec clips -> Google Cloud
# # Directory where you want to save all podcasts (This need to change for every person)


# List of audio files with their ad times and podcast names for mp3/wav files:
# 1: Audio name file with the extation
# 2: Period in seconds where the ad starts and ends
# 3: Output name: name podcast and episode


podcast_files_mp3_wav = [
    (os.path.join(base_directory, "When Bitter Becomes Sweet.mp3"), [32, (60+8)], "whenbitterbcamessweet"),
    # (os.path.join(base_directory, "What's Hidden in Your Words.mp3"), [(20*60+25), (21*60+10), (38*60+10), (38*60+37)], "whatishiddeninyourwordsEp01"),
    (os.path.join(base_directory,"The Problem With Fancy Grocery Stores ft. Gwynedd Stuart.mp3"), [0, (60+58), (60*24+20), (60*26+52), (60*60+52), ((60*60)+(60*4+29)), ((60*60)+(60*23+3)), ((60*60)+(60*24+44))], "theproblemwithfancygrocerystoresftgwyneddstuartEp01"),
    (os.path.join(base_directory, "When Bitter Becomes Sweet.mp3"), [32, (60+8)], "whenbitterbcamessweet"),
    # (os.path.join(base_directory, "Surviving a Hurricane,mp3"), [0, (2*60), (56*60), (56*60+32), ((60*60)+(60*8+29)), ((60*60)+(60*10+25)), ((60*60)+(60*40+24)), ((60*60)+(60*40+53))], "survivingahurricaneEp01"),
            #("podcast1.wav", [0,0], "podcastep1")
]

# Loop through each file and process mp3:
for file_name, ad_list, podcast_name in podcast_files_mp3_wav:
    result = split_files(file_name, ad_list, podcast_name, output_directory)
    print(f'Processing {podcast_name}: {result}')
