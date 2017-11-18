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
  pydaq=current \
  pycdb=current \
  pyami=current \
  pyqt=5.6 \
  pyqtgraph \
  pyepics=3.2.7 \
  bluesky \
  ophyd \
  jupyter \
  opencv \
  xarray \
  simplejson \
  flake8 \
  pytest \
  pytest-timeout \
  sphinx \
  sphinx_rtd_theme \
  doctr \
  cookiecutter \
  conda-wrappers
