import pandas as pd
import numpy as np
import os
from pydub import AudioSegment


def remove_ads_from_podcast(podcast_file, ad_segments):
    """
    Removes the ad segments from the podcast and saves two files:
    - An ad-free podcast file
    - A file with only the ad segments
    podcast_file: Path to the podcast audio file
    ad_segments: List of tuples with (start_time, end_time) of ads in seconds
    """

    # Load
    podcast = AudioSegment.from_file(podcast_file) # Load the podcast file
    podcast_duration = len(podcast)

    # Initialize segments for the ad-free podcast and for the ads only
    clean_podcast = AudioSegment.empty()
    ads_only = AudioSegment.empty()
    current_time = 0

    for ad_start, ad_end in ad_segments:
        ad_start_ms = ad_start * 1000 # Convert to milliseconds
        ad_end_ms = ad_end * 1000
        # Add non-ad segment to the clean podcast
        clean_podcast += podcast[current_time:ad_start_ms]

        # Add ad segment to the ads_only file
        ads_only += podcast[ad_start_ms:ad_end_ms]

        # Update the current time
        current_time = ad_end_ms

    # Add the last segment of the podcast
    clean_podcast += podcast[current_time:podcast_duration]  # Add the last segment of the podcast

    return clean_podcast, ads_only
