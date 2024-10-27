import pandas as pd
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from podcast_ad_skipper.model import download_model_from_gcs
import numpy as np
import tensorflow as tf
from keras import Model, Sequential, layers, regularizers, optimizers, applications, models
from podcast_ad_skipper.params import *
from podcast_ad_skipper.google_cloud import download_model_from_gcs

#Basic structure of API - not yet functioning

app = FastAPI()

gcs_uri = f"gs://{BUCKET_NAME_MODEL}/trained_model"


app.state.model = download_model_from_gcs(gcs_uri)
model = app.state.model

@app.get("/predict")
def predict(spectrogram: np.ndarray, model):
# FROM CODE IN FRONT END
    model = app.state.model
    X_pred_preprocessed = None
    prediction = model.predict(X_pred_preprocessed)
    return prediction


@app.get("/")
def root():
    return {
    'greeting': 'Hello'
    }
