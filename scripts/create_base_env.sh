#!/bin/bash
# Creates a "latest" environment from key packages
if [ -z $1 ]; then
  echo "Usage: create_base_env.sh [envname]"
  exit
else
  ENVNAME="${1}"
fi
conda create -y --name $ENVNAME \
  python=3.6 \
  ipython \
  hutch-python=0.1.0 \
  pydaq=current \
  pycdb=current \
  pyami=current \
  pydm=1.0.0 \
  pyepics=3.2.7 \
  jupyter \
  opencv \
  xarray \
  simplejson \
  flake8 \
  coloredlogs \
  pytest \
  pytest-timeout \
  sphinx \
  sphinx_rtd_theme \
  doctr \
  cookiecutter \
  versioneer \
  conda-wrappers

source activate $ENVNAME
pip install QDarkStyle
source deactivate
