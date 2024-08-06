#!/bin/bash

set -e

for i in *.ipynb; do
    papermill --request-save-on-cell-execute --autosave-cell-every 10 $i work/$i
done
