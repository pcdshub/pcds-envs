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

conda activate $ENVNAME

# Special DAQ installs that rely on our filesystem
FILE_CHANNEL="/reg/g/pcds/pyps/conda/channel"
if [ -d "$FILE_CHANNEL" ]; then
  conda install pydaq=current -c "file://$FILE_CHANNEL"
fi

# pip install where missing from conda
# we can convert these into conda recipes later
pip install QDarkStyle
pip install mysqlclient

conda deactivate
