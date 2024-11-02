import pandas as pd
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from podcast_ad_skipper.model import download_model_from_gcs
import numpy as np
import tensorflow as tf
from keras import Model, Sequential, layers, regularizers, optimizers, applications, models
from podcast_ad_skipper.params import *

#Basic structure of API - not yet functioning

app = FastAPI()

# Download mod
gcs_uri = f"gs://{BUCKET_NAME_MODEL}/latest_trained_model.h5"
app.state.model = download_model_from_gcs(gcs_uri)


@app.get("/predict")
def predict(spectrogram):
    model = app.state.model
    prediction = model.predict(spectrogram)
    return prediction
    # return {
    # 'greeting': 'Hello predict'
    # }

@app.get("/")
def root():
    return {
    'greeting': 'Hello'
    }
