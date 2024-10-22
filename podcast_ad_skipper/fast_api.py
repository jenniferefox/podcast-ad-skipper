import pandas as pd
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

#Basic structure of API - not yet functioning

app = FastAPI()

# app.state.model = load_model()
@app.get("/predict")
def predict(
        podcast_link: str
    ):
    """
    Takes podcast file, runs model and outputs podcast without ads.
    """

    X_pred = #define this
    X_preproc = #preprocess X_pred

    model = app.state.model
    assert model is not None
    y_pred = float(model.predict(X_preproc))

    return {
    'no_ad_podcast': y_pred
    }

@app.get("/")
def root():
    return {
    'greeting': 'Hello'
    }
