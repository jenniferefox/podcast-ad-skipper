import librosa

#Create spectrogram from wav file
def create_spectrogram(audio_file):
    #y is an array representing the frequency of the audio signal at each sample.
    #sr is the sampling rate (samples per second),
    y, sr = librosa.load(audio_file)
    spectrogram = librosa.stft(y)

    #Transforms to decibel scale (logarithmic), which gives more emphasis to amplitude changes in high volumes
    spectrogram_db = librosa.amplitude_to_db(abs(spectrogram))
    return spectrogram_db
