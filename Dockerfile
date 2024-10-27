FROM python:3.10.6-buster
WORKDIR /app
COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt
COPY podcast_ad_skipper podcast_ad_skipper
COPY setup.py setup.py
RUN pip install .
ENV PORT=8000
CMD uvicorn podcast_ad_skipper.fast_api:app --host 0.0.0.0 --port $PORT

# --port $PORT
