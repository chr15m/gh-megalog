#!/bin/bash

. ./virtualenv/bin/activate
./list-all-commits.py "$@" | sort -rs -t$'\t' -k2
