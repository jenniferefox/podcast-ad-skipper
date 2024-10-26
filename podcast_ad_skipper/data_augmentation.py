from audiomentations import Compose, TimeMask, SpecFrequencyMask, PitchShift, AddGaussianNoise
import numpy as np
import matplotlib.pyplot as plt

def augment_audiodata_by_4(list_of_spectrogram_files, sr=16000):
    '''
    Augments current dataset x 4:
    1. Original wav, with time masking
    2. Original wav with frequency masking
    3. Wav with added noise and pitch shift with time masking
    4. Wav with added noise and pitch shift with frequency masking
    '''
    #Adds timemask
    augment_timemask = Compose([
        TimeMask(min_band_part=0.1, max_band_part=0.15, fade=True, p=1.0)
        ])

    #Adds frequencymask
    augment_frequencymask = SpecFrequencyMask(p=1.0)

    #Adds noise, changes pitch, adds timemask
    augment_noise_pitch_timemask = Compose([
        TimeMask(min_band_part=0.1, max_band_part=0.15, fade=True, p=1.0),
        AddGaussianNoise(min_amplitude=0.001, max_amplitude=0.015, p=0.5),
        PitchShift(min_semitones=-4, max_semitones=4, p=0.5)
        ])

    #Adds noise, changes pitch, adds timefrequencymask
    augment_noise_pitch_frequencymask = Compose([
        AddGaussianNoise(min_amplitude=0.001, max_amplitude=0.015, p=0.5),
        PitchShift(min_semitones=-4, max_semitones=4, p=0.5),
        ])

    for file in list_of_spectrogram_files:
        timemask_spectrogram = augment_timemask(samples=file,sample_rate=sr)
        frequencymask_spectrogram = augment_frequencymask(file)
        noise_pitch_timemask_spectrogram = augment_noise_pitch_timemask(samples=file, sample_rate=sr)
        noise_pitch_frequencymask_spectrogram = augment_frequencymask(augment_noise_pitch_frequencymask(samples=file, sample_rate=sr))
        np.array(timemask_spectrogram, frequencymask_spectrogram, noise_pitch_timemask_spectrogram, noise_pitch_frequencymask_spectrogram)
