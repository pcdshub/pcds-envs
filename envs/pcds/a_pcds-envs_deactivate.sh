#!/bin/bash
# After all other deactivate scripts, activate the pcds central epics env
# Deactivate scripts are run in reverse alphabetical order
# This helps usage of external epics tools after the conda env is deactivated
# Technically this is a workaround for the epics-base deactivate script
if [ -z "${SETUP_SITE_TOP}" ]; then
    SETUP_SITE_TOP='/cds/group/pcds/setup'
fi
EPICS_ENV_SCRIPT="${SETUP_SITE_TOP}/epicsenv-cur.sh"
if [ -x "${EPICS_ENV_SCRIPT}" ]; then
    source "${EPICS_ENV_SCRIPT}"
fi

unset QT_XCB_GL_INTEGRATION
