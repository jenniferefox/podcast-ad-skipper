import os

# GCS
BUCKET_NAME = os.environ.get("BUCKET_NAME")
BUCKET_NAME_MODEL = os.environ.get("BUCKET_NAME_MODEL")
GCP_PROJECT_ID = os.environ.get("GCP_PROJECT_ID")
GCP_REGION = os.environ.get("GCP_REGION")
GOOGLE_CLOUD_SERVICE_ACCOUNT = os.environ.get("GOOGLE_CLOUD_SERVICE_ACCOUNT")
# Compute Engine
INSTANCE = os.environ.get("INSTANCE")
INSTANCE_NAME_PRO=os.environ.get("INSTANCE_NAME_PRO")

# BigQuery
BQ_REGION = os.environ.get("BQ_REGION")
BQ_DATASET = os.environ.get("BQ_DATASET")
BQ_TABLE = os.environ.get("BQ_TABLE")

GAR_IMAGE = os.environ.get("GAR_IMAGE")
IMAGE_ID = os.environ.get("IMAGE_ID")
IMAGE_TAB = os.environ.get("IMAGE_TAB")


GCP_PREFIXES = [
    "billionairepersonalitydisorder",
    "bitcoinminingdecentralizationwiththedatumprotocolatoceanmining",
    "ceo181",
    "changesinthebigapple",
    "differentdays",
    "donaldtrumpjoinstheshow",
    "dreamingofpolarnightinsvalbard",
    "drewbarrymoreasksaboutboogers",
    "electionspecial",
    "farking&thelyingjester",
    "guenthersteinerlifeontheothersideoff1",
    "israelatwaroneyearon",
    "knowingwhoyouare",
    "nstaaf1",
    "offmenu263",
    "parentingHell908",
    "quintabrunson",
    "rabbitceojesselyuisnotthinkingtoofaradead",
    "rupikauropensupifetinvisible",
    "survivingahurricaneEp01",
    "theproblemwithfancygrocerystoresftgwyneddstuartEp01",
    "whatishiddeninyourwordsEp01",
    "whenbitterbcamessweet",
]
