#!/bin/bash
# After all other activate scripts, activate the pcds central epics env
# Activate scripts are run in alphabetical order.
# This helps usage of external epics tools while the conda env is active
# Technically this is a workaround for the epics-base activate script
if [ -z "${SETUP_SITE_TOP}" ]; then
    SETUP_SITE_TOP='/cds/group/pcds/setup'
fi
EPICS_ENV_SCRIPT="${SETUP_SITE_TOP}/epicsenv-cur.sh"
if [ -x "${EPICS_ENV_SCRIPT}" ]; then
    source "${EPICS_ENV_SCRIPT}"
fi

