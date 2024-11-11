# Podcast Ad Skipper

## Overview
Podcast Ad Skipper is a Python-based machine learning project that allows users to download their favourite podcasts, automatically detect advertisements, and remove them. This results in a seamless listening experience where users can enjoy their podcasts without interruptions.

## Features
- Download your favorite podcasts.
- Automatic detection of ads within podcast episodes.
- Removal of detected ads.
- Assembly of the final podcast episode for uninterrupted listening.

## Requirements
- Python 3.10.6
- Docker (for containerized deployment)

## Installation

### Install ffmpeg
To install `ffmpeg`, use Homebrew:
```
brew install ffmpeg
```

### Using `setup.py`
1. Clone the repository:
   ```
   git clone https://github.com/jenniferefox/podcast-ad-skipper.git

   cd podcast-ad-skipper
   ```

2. Install the required packages:
   ```
   python setup.py install
   ```

### Using Docker
1. Build the Docker image:
   ```
   docker build -t podcast-ad-skipper .
   ```

2. Run the Docker container:
   ```
   docker run -it podcast-ad-skipper
   ```

<!-- ## Setup for `split_files` Function
To use the `split_files` function, you need to create the following directories:

```
mkdir /Users/XXX/code/jenniferefox/podcast-ad-remover/raw_data/5_sec_clips
mkdir /Users/XXX/code/jenniferefox/podcast-ad-remover/raw_data/full_podcast
```
**Note:** Replace `XXX` with your username.
- `5_sec_clips`: This folder will store the 5-second clips.
- `full_podcast`: This folder will save the full podcasts. -->

## System Design
The system is designed to leverage Google Cloud Platform (GCP) for scalable and efficient podcast processing. Below is a diagram illustrating the architecture:

flowchart TD
    Start["Start"] --> Upload["Upload Wav Audio Files to Google Cloud Storage"]
    Upload --> Convert["Convert to Spectrograms"]
    Convert --> Store["Store Spectrograms as Numpy arrays in Google BigQuery"]
    Store --> Train["Input data to train CNN Model"]
    Train --> End["End"]

    style Start fill:#66BB6A,stroke:#4CAF50,color:#FFFFFF
    style Upload fill:#29B6F6,stroke:#0288D1,color:#FFFFFF
    style Convert fill:#FFCA28,stroke:#FFB300,color:#FFFFFF
    style Store fill:#AB47BC,stroke:#8E24AA,color:#FFFFFF
    style Train fill:#EF5350,stroke:#E53935,color:#FFFFFF
    style End fill:#66BB6A,stroke:#4CAF50,color:#FFFFFF



## License
This project is licensed under the MIT License.
