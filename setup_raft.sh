#!/bin/bash

git clone --no-checkout --depth=1 --filter=tree:0 https://github.com/cedricvidal/gorilla.git --branch upstream-merge-prep --single-branch
cd gorilla/
git sparse-checkout set --no-cone raft
git checkout
