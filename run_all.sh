#!/bin/bash

set -e

mkdir -p work
rm -rf work/notebooks
mkdir -p work/notebooks
for i in *.ipynb; do
    papermill --request-save-on-cell-execute --autosave-cell-every 10 $i work/notebooks/$i ${*}
done
