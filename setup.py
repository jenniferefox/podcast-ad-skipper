from setuptools import find_packages
from setuptools import setup

with open("requirements.txt") as f:
    content = f.readlines()
requirements = [x.strip() for x in content if "git+" not in x]

setup(name='podcast-ad-skipper',
      version="0.0.12",
      description="Podcast Ad Skipper",
      license="MIT",
    #   author="Jenny, Leandro, Irene",
      author_email="",
      #url="https://github.com/jenniferefox/podcast-ad-skipper",
      install_requires=requirements,
      packages=find_packages(),
      test_suite="tests",
      # include_package_data: to install data from MANIFEST.in
      include_package_data=True,
      zip_safe=False)
