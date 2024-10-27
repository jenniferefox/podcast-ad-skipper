FROM python:3.10.6-buster
WORKDIR /app
COPY requirements_for_docker_image.txt requirements_for_docker_image.txt
RUN pip install -r requirements_for_docker_image.txt
COPY podcast_ad_skipper podcast_ad_skipper
COPY setup.py setup.py
RUN pip install .
CMD uvicorn app.fast_api:app --host 0.0.0.0 --port $PORT
