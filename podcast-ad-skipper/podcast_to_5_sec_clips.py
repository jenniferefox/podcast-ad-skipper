from pydub import AudioSegment

# This function takes 3 inputs:
# 1. The audio file that is to be split up
# 2. A list of integers which shows when each ad starts and ends. The list must be an even length to include the in and out time of each ad.
# 3. the name of the podcast, to be used in the final file output name
# *IMPORTANT* Before running this, make sure that your mp3 file is saved in the same folder. You may need to copy this in your raw_data folder

def split_filemp3(original_file, ad_list, podcast_name):

    #import original_file
    new_audio = AudioSegment.from_mp3(original_file)

    #save duration
    duration = int(new_audio.duration_seconds)

    #set default to no_ad
    is_ad = '0'

    #if the ad_list doesn't start with 0, then the ads don't start straight away.
    #in this case, insert '0' first in the list so that a segment is created at the start.
    if ad_list[0] != 0:
        ad_list.insert(0, 0)
        is_ad = '1'
    #add duration at the end so that the end segments can be made.
    if ad_list[-1] != duration:
        ad_list.append(duration)
    #Go through each segement in the list, label whether the section is an ad or not
    for index in range(0,len(ad_list)-1):
        start = ad_list[index]
        end = ad_list[index+1]
        if is_ad == '1':
            is_ad = '0'
        else:
            is_ad = '1'
        #go through each second in the segment and create a new 5 second clip from here.
        #stop before the end of the segment so that only 5 second clips are created
        for tc in range(start, (end-4)):
            start_clip = tc*1000 #pydub works with milliseconds, so seconds are converted here
            end_clip = (tc+5)*1000
            new_audio[start_clip:end_clip].export(
                f'{podcast_name}_{is_ad}_{tc}.wav',
                format='wav')
    is_ad = '0'
    return 'finished'


# Same function but for wav files, outputs mp3 to be consistent

def split_filewav(original_file, ad_list, podcast_name):

    #import original_file
    new_audio = AudioSegment.from_wav(original_file)

    #save duration
    duration = int(new_audio.duration_seconds)

    #set default to no_ad
    is_ad = '0'

    #if the ad_list doesn't start with 0, then the ads don't start straight away.
    #in this case, insert '0' first in the list so that a segment is created at the start.
    if ad_list[0] != 0:
        ad_list.insert(0, 0)
        is_ad = '1'
    #add duration at the end so that the end segments can be made.
    if ad_list[-1] != duration:
        ad_list.append(duration)
    #Go through each segement in the list, label whether the section is an ad or not
    for index in range(0,len(ad_list)-1):
        start = ad_list[index]
        end = ad_list[index+1]
        if is_ad == '1':
            is_ad = '0'
        else:
            is_ad = '1'
        #go through each second in the segment and create a new 5 second clip from here.
        #stop before the end of the segment so that only 5 second clips are created
        for tc in range(start, (end-4)):
            start_clip = tc*1000 #pydub works with milliseconds, so seconds are converted here
            end_clip = (tc+5)*1000
            new_audio[start_clip:end_clip].export(
                f'{podcast_name}_{is_ad}_{tc}.wav',
                format='wav')
    is_ad = '0'
    return 'finished'
