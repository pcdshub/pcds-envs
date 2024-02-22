#!/bin/bash
# Please add stdout to this file when you extend it to help debug
PLUGIN_SOURCE="${DESIGNER_PLUGIN:-/cds/group/pcds/pyps/conda/designer_fix/libpyqt5.so}"
PLUGIN_DEST="${CONDA_PREFIX}/plugins/designer/libpyqt5.so"
if [ -f "${PLUGIN_DEST}" ]; then
    echo "There is already a file at ${PLUGIN_DEST}, skipping."
else
    if [ -f "${PLUGIN_SOURCE}" ]; then
        echo "Using precompiled designer plugin file from ${PLUGIN_SOURCE}"
        cp "${PLUGIN_PATH}" "${PLUGIN_DEST}"
    else
        echo "Could not find precompiled designer plugin file at ${PLUGIN_SOURCE}"
    fi
fi
