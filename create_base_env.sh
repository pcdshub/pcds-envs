#!/bin/bash
# Creates a "latest" environment from key packages
if [ -z $1 ]; then
  echo "Usage: create_base_env.sh [envname]"
  exit
else
  ENVNAME="${1}"
fi
conda create --name $ENVNAME \
  python=3.6 \
  ipython \
  pydaq=current \
  pycdb=current \
  pyami=current \
  bluesky \
  ophyd \
  jupyter \
  opencv \
  xarray \
  simplejson \
  flake8 \
  pytest \
  pytest-timeout \
  conda-wrappers
