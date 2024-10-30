
default: pylint pytest

pylint:
	find . -iname "*.py" -not -path "./tests/*" | xargs -n1 -I {}  pylint --output-format=colorized {}; true

pytest:
	PYTHONDONTWRITEBYTECODE=1 pytest -v --color=yes

split_clip:
	@python podcast_ad_skipper/split_clips.py

get_fuatures_model:
	@python podcast-ad-skipper/data_preparation.py

install:
	pip install -e .

run_api:
	uvicorn podcast_ad_skipper.fast_api:app --reload
