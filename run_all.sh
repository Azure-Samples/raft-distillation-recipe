#!/bin/bash

set -e

mkdir -p work
rm -rf work/notebooks
mkdir -p work/notebooks
for i in $(find ./infra/python -type f -name "*.ipynb" -maxdepth 1 | sort) $(find . -type f -name "*.ipynb" -maxdepth 1 | sort); do
    echo papermill --request-save-on-cell-execute --autosave-cell-every 10 $i work/notebooks/$i ${*}
done
