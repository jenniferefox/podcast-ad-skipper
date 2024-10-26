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
    base_directory = 'raw_data/new_podcast_ceo' # Add the full audio file here
    output_directory = 'raw_data/5_sec_clips' # Temporally store for the 5 sec clips -> Google Cloud
    # # Directory where you want to save all podcasts (This need to change for every person)

    # List of audio files with their ad times and podcast names for mp3/wav files:
    # 1: Audio name file with the extation
    # 2: Period in seconds where the ad starts and ends
    # 3: Output name: name podcast and episode

    podcast_files_mp3_wav = [
        # (os.path.join(base_directory, "CEO181.mp3"), [0, 44, (9*60)+39, (11*60)+21], "ceo181"),
        # (os.path.join(base_directory, "OffMenu263.mp3"), [0,(60*2)+43,(3*60)+58, (4*60)+19, (33*60)+31, (35*60)+31,(54*60)+50, (56*60)+19,(77*60)+55, (78*60)+52, (79*60)+29, (80*60)+47], "offmenu263"),
        # (os.path.join(base_directory, "ParentingHell908.mp3"), [37, (60+15), (55*60)+36, (57*60)+4], "parentingHell908"),
        # (os.path.join(base_directory, "NSTAAF_Radioactivejenga.mp3"), [60+34,(60*2)+5,(60*17)+42,(20*60)+55,(48*60)+35,(50*60)+5,(58*60)+4,(59*60)+27], "nstaaf1"),
        # (os.path.join(base_directory, "When Bitter Becomes Sweet.mp3"), [32, (60+8)], "whenbitterbcamessweet"),
        # (os.path.join(base_directory, "What's Hidden in Your Words.mp3"), [(20*60+25), (21*60+10), (38*60+10), (38*60+37)], "whatishiddeninyourwordsEp01"),
        # (os.path.join(base_directory, "The Problem With Fancy Grocery Stores ft. Gwynedd Stuart.mp3"), [0, (60+58), (60*24+20), (60*26+52), (60*60+52), ((60*60)+(60*4+29)), ((60*60)+(60*23+3)), ((60*60)+(60*24+44))], "theproblemwithfancygrocerystoresftgwyneddstuartEp01"),
        # (os.path.join(base_directory, "Rabbit CEO Jesse Lyu is not thinking too far ahead.mp3"), [0, (2*60), (24*60+12), (26*60+50), (60*60+51), ((60*60)+(4*60+30)), ((60*60)+(23*60+3)), ((60*60)+(24*60+44))  ], "rabbitceojesselyuisnotthinkingtoofaradead"),
        # (os.path.join(base_directory, "Surviving a Hurricane.mp3"), [0, (2*60), (56*60), (56*60+32), ((60*60)+(60*8+29)), ((60*60)+(60*10+25)), ((60*60)+(60*40+24)), ((60*60)+(60*40+53))], "survivingahurricaneEp01"),
        # (os.path.join(base_directory, "Rupi Kaur Opens Up -I Felt Invisible- How To Transcend Trauma & Find Your Self-Worth.mp3"), [(60+21), (2*60+59), (22*60+20), (24*60), (43*60+50), (45*60), ((60*60)+(4*60+20)), ((60*60)+(5*60+30)), ((60*60)+(20*60+50)), ((60*60)+(22*60))], "rupikauropensupifetinvisible"),
        # (os.path.join(base_directory, "Quinta Brunson.mp3"), [0, 45, ((60*60)+(6*60+35)), ((60*60)+(7*60+45))], "quintabrunson"),
        # (os.path.join(base_directory, "Israel at War One Year On.mp3"), [0, (2*60+40), (58*60+18), (59*60+49)], "israelatwaroneyearon"),
        # (os.path.join(base_directory, "Guenther Steiner life on the other side of F1.mp3"), [(9*60+50), (11*60), (19*60), (20*60+30), (32*60), (33*60+15)], "guenthersteinerlifeontheothersideoff1"),
        # (os.path.join(base_directory, "Fat King & The Lying Jester.mp3"), [0, 60+5, (22*60+15), (24*60+45)], "farking&thelyingjester"),
        # (os.path.join(base_directory, "Election Special.mp3"), [0, 60,  (20*60+20), (21*60+50), (26*60+50), (28*60+20), (42*60+30), (48*60)], "electionspecial"),
        # (os.path.join(base_directory, "Drew Barrymore asks about boogers.mp3"), [0,  (2*60+15), (17*60+25), (19*60+12), (31*60+20), (32*60+30)], "drewbarrymoreasksaboutboogers"),
        # (os.path.join(base_directory, "Dreaming of Polar Night in Svalbard.mp3"), [0, 60+40], "dreamingofpolarnightinsvalbard"),
        # (os.path.join(base_directory, "Donald Trump Joins The Show!.mp3"), [(4*60+25), (5*60+30), (12*60+5), (13*60+5), (26*60+45), (27*60+55)], "donaldtrumpjoinstheshow"),
        # (os.path.join(base_directory, "Different Days.mp3"), [0, 60,  (40*60+20), (40*60+50), ((60*60)+(23*60+45)), ((60*60)+(24*60+18))], "differentdays"),
        # (os.path.join(base_directory, "Changes in the Big Apple.mp3"), [0, 30,  (15*60+50), (17*60+15), (22*60+30), (22*60+50), (35*60+10), (32*60+45)], "changesinthebigapple"),
        # (os.path.join(base_directory, "Bitcoin Mining Decentralization with the Datum Protocol at Ocean Mining.mp3"), [0, (60+25), (14*60+20), (18*60), (30*60+50), (33*60+45), (59*60+30), (60*60+2)], "bitcoinminingdecentralizationwiththedatumprotocolatoceanmining"),
        # (os.path.join(base_directory, "Billionaire Personality Disorder.mp3"), [0, 30, (23*60+20), (25*60+5), (60*60+50), (60*60+95), ((60*60)+(36*60+5)), ((60*60)+(37*60+45))], "billionairepersonalitydisorder"),
        # (os.path.join(base_directory, "Knowing who you are.mp3"), [0, 60, (49*60+25), (52*60+41), ((60*60)+(7*60+30)),  ((60*60)+(11*60+8))], "knowingwhoyouare"),
        (os.path.join(base_directory, "Glucose Goddess -  The Scary New Research On Sugar!.mp3"), [((60*60)+(16*60+30)), ((60*60)+(18*60+25)), ((60*60)+(38*60+20)), ((60*60)+(39*60+15))], "glucosegoddess"),
        (os.path.join(base_directory, "Gabrielle Lyon - The Anti-Obesity Doctor,  If You Don't Exercise.mp3"), [60+35, 2*60+5, ((60*60)+(20*60+30)), ((60*60)+(22*60+25)), ((60*60)+(52*60+40)), ((60*60)+(53*60+35))], "gabriellelyon"),
        (os.path.join(base_directory, "Eye Doctor - They're Lying To You About Blue Light.mp3"), [((60*60)+(18*60+25)), ((60*60)+(20*60+15)), ((60*60)+(39*60+50)), ((60*60)+(40*60+55))], "eyedoctor"),
        (os.path.join(base_directory, "Ramit Sethi - Never Split The Bill, It's A Red Flag & Renting Isn't Wasting Money.mp3"),	[((60*60)+(38*60+35)), ((60*60)+(40*60+20)), ((60*60)+(48*60+15)), ((60*60)+(49*60+10))], "ramitsethi"),
        (os.path.join(base_directory, "Trevor Noah - My Depression Was Linked To ADHD.mp3"), [((120*60)+(17*60)), ((120*60)+(18*60+55)), ((60*60)+(48*60+15)), ((60*60)+(49*60+10))], "trevornoah"),
        (os.path.join(base_directory, "Boris Johnson - They Were Looking at Engineering The Virus.mp3"), [((60*60)+(12*60+40)), ((60*60)+(14*60+40)), ((60*60)+(51*60+50)), ((60*60)+(52*60+45))], "borisjohnson"),
    ]

    # Loop through each file and process mp3:
    for file_name, ad_list, podcast_name in podcast_files_mp3_wav:
        result = split_files(file_name, ad_list, podcast_name, output_directory)
        print(f'Processing {podcast_name}: {result}')
