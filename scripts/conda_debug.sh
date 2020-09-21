#!/bin/bash
# Run this script if the conda build fails and you don't know why.
# This script creates a conda-debug environment, installing packages
# one-by-one. In this way it becomes more apparent which packages are
# incompatible, since the output from a failure to install 1 package
# is more readable than the output for failing to install 50.
if [ -z "${1}" ]; then
  echo "Usage: conda_debug.sh [env]"
  exit
else
  ENV="${1}"
fi
set -e
source "$(dirname `which conda`)/../etc/profile.d/conda.sh"

conda create -y --name conda-debug python=3.6
conda activate conda-debug

PACKAGES="../envs/${ENV}/conda-packages.txt"
cat "${PACKAGES}" | while read line
do
  conda install -y "${line}" 2>&1 | tee -a conda_debug.log
done
echo "Finished conda debug with no errors."
