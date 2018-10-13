#!/bin/bash
# Creates a "latest" environment from key packages
if [ -z $1 ]; then
  echo "Usage: create_base_env.sh [envname]"
  exit
else
  ENVNAME="${1}"
fi
set -e
source "$(dirname `which conda`)/../etc/profile.d/conda.sh"
conda create -y --name $ENVNAME --file packages.txt
conda deactivate
