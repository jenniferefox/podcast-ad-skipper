# Podcast Ad Skipper

## Overview
Podcast Ad Skipper is a Python-based project that allows users to download their favourite podcasts, automatically detect advertisements, and remove them. This results in a seamless listening experience where users can enjoy their podcasts without interruptions.

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
The system is designed to leverage Google Cloud Platform (GCP) for scalable and efficient podcast processing.

## License
This project is licensed under the MIT License. See the LICENSE file for more details. --> just an example!!!

