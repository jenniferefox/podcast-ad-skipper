
default: pylint pytest 

pylint:
	find . -iname "*.py" -not -path "./tests/*" | xargs -n1 -I {}  pylint --output-format=colorized {}; true

pytest:
	PYTHONDONTWRITEBYTECODE=1 pytest -v --color=yes


split_clip:
	python podcast-ad-skipper/podcast_to_5_sec_clips.py
