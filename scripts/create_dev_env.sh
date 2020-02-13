#!/bin/bash
# Creates a latest + dev environment
# Picks newest tags of most things and master checkout of dev things
if [ $# -lt 3 ]; then
  echo "Usage: create_dev_env.sh [base] [envname] [devdir] [pkgs]"
  exit
else
  base="${1}"
  envname="${2}"
  devdir="${3}"
  shift
  shift
  shift
  pkgs="${@}"
fi
set -e
echo "Setting up conda env in script"
source "$(dirname `which conda`)/../etc/profile.d/conda.sh"
envdir="../envs/${base}"
echo "Creating new env ${envname}"
conda create -y --name "${envname}" --file "${envdir}/conda-packages.txt"
echo "Activating env ${envname}"
conda activate "${envname}"
echo "Installing any scheduled pip packages to ${envname}"
pip install -r "${envdir}/pip-packages.txt"
echo "Remove incompatible package" # TODO delete this
conda remove -y pmgr # TODO delete this after issue resolved
echo "Changing to directory ${devdir}"
cd "${devdir}"
for pkg in $pkgs
do
  set +e
  echo "Attempting to clone ${pkg} from slaclab..."
  git clone "git@github.com:slaclab/${pkg}"
  if [ "$?" -ne "0" ]; then
    echo "Attempting to clone ${pkg} from pcdshub..."
    git clone "git@github.com:pcdshub/${pkg}"
    if [ "$?" -ne "0" ]; then
      set -e
      echo "Attempting to clone ${pkg} from bluesky..."
      git clone "git@github.com:bluesky/${pkg}"
    fi
  fi
  set -e
  echo "Removing tagged ${pkg} from environment"
  conda remove -y --force "${pkg}"
  echo "Installing ${pkg} master branch in dev mode"
  pip install -e "${pkg}"
done
