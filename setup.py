import pathlib
from setuptools import setup, find_packages

HERE = pathlib.Path(__file__).parent

VERSION = "1.4.3"
PACKAGE_NAME = "pyrfu"
AUTHOR = "Louis RICHARD"
AUTHOR_EMAIL = "louir@irfu.se"
URL = "https://github.com/louis-richard/irfu-python"

LICENSE = "MIT License"
DESCRIPTION = "Python Space Physics Environment Data Analysis"
LONG_DESCRIPTION = (HERE / "README.md").read_text()
LONG_DESC_TYPE = "text/markdown"

INSTALL_REQUIRES = [
      "astropy",
      "cycler",
      "python-dateutil",
      "matplotlib",
      "numpy",
      "pandas",
      "psychopy",
      "pvlib",
      "pyfftw",
      "scipy",
      "seaborn",
      "sfs",
      "spacepy",
      "tqdm",
      "xarray"
]

PYTHON_REQUIRES = ">=3.7"

setup(name=PACKAGE_NAME,
      version=VERSION,
      description=DESCRIPTION,
      long_description=LONG_DESCRIPTION,
      long_description_content_type=LONG_DESC_TYPE,
      author=AUTHOR,
      license=LICENSE,
      author_email=AUTHOR_EMAIL,
      url=URL,
      install_requires=INSTALL_REQUIRES,
      python_requires=PYTHON_REQUIRES,
      packages=find_packages(),
      include_package_data=True,
      )
