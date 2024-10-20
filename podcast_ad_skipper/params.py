import os

BUCKET_NAME  = os.environ.get("BUCKET_NAME")
GCP_PROJECT_ID = os.environ.get("GCP_PROJECT_ID")
GCP_REGION = os.environ.get("GCP_REGION")

PREFIXES_PODCAST_AD_SKIPPER = [
    'billionairepersonalitydisorder',
    'bitcoinminingdecentralizationwiththedatumprotocolatoceanmining',
    'ceo181',
    'changesinthebigapple',
    'differentdays',
    'donaldtrumpjoinstheshow',
    'dreamingofpolarnightinsvalbard',
    'drewbarrymoreasksaboutboogers',
    'electionspecial',
    'farking&thelyingjester',
    'guenthersteinerlifeontheothersideoff1',
    'israelatwaroneyearon',
    'knowingwhoyouare',
    'nstaaf1',
    'offmenu263',
    'parentingHell908',
    'quintabrunson',
    'rabbitceojesselyuisnotthinkingtoofaradead',
    'rupikauropensupifetinvisible',
    'survivingahurricaneEp01',
    'theproblemwithfancygrocerystoresftgwyneddstuartEp01',
    'whatishiddeninyourwordsEp01',
    'whenbitterbcamessweet'
]
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
