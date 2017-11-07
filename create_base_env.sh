#!/bin/bash
# Creates a "latest" environment from key packages
if [ -z $1 ]; then
  echo "Usage: create_base_env.sh [envname]"
  exit
else
  ENVNAME="${1}"
fi
conda create --name $ENVNAME python=3.6 ipython jupyter opencv simplejson bluesky ophyd flake8 pytest pytest-timeout
