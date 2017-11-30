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
  pydm \
  pcds-devices=0.2.0 \
  pswalker=0.2.0 \
  lightpath=0.2.1 \
  psbeam=0.0.3 \
  pydaq=current \
  pycdb=current \
  pyami=current \
  pyepics=3.2.7 \
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
