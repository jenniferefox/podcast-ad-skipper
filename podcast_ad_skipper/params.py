import os

# GCS
BUCKET_NAME  = os.environ.get("BUCKET_NAME")
GCP_PROJECT_ID = os.environ.get("GCP_PROJECT_ID")
GCP_REGION = os.environ.get("GCP_REGION")


# Compute Engine
INSTANCE= os.environ.get("INSTANCE")

# BigQuery
BQ_REGION = os.environ.get("BQ_REGION")
BQ_DATASET = os.environ.get("BQ_DATASET")
BQ_TABLE = os.environ.get("BQ_TABLE")



GCP_PREFIXES = ['billionairepersonalitydisorder/',
'bitcoinminingdecentralizationwiththedatumprotocolatoceanmining/',
'ceo181/']
