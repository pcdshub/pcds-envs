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
  hutch-python \
  pydaq=current \
  pycdb=current \
  pyami=current \
  pydm \
  pyepics \
  pyca \
  psdm_qs_cli \
  jupyter \
  opencv \
  pandas \
  xarray \
  simplejson \
  flake8 \
  coloredlogs \
  pyfiglet \
  pytest \
  pytest-timeout \
  sphinx \
  sphinx_rtd_theme \
  doctr \
  cookiecutter \
  versioneer \

source activate $ENVNAME
pip install QDarkStyle
source deactivate
