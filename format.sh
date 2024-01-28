#!/usr/bin/env bash

# This script formats the codebase using black and isort.

dirs="migrations vending_machine ./*.py"

for dir in $dirs; do
    echo "Formatting $dir"
    black "$dir"
    isort "$dir" --profile black
done
