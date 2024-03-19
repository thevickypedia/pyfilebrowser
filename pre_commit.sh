#!/bin/bash
# shellcheck disable=SC2155
export root="$(pwd)"  # root is mandatory, so set to pwd
rm -rf docs && mkdir docs
mkdir -p doc_gen/_static  # Create a _static directory if unavailable
cp README.md doc_gen  # Copy readme file to doc_gen
cd doc_gen && make clean html  # cd into doc_gen and create the runbook
mv _build/html/* ../docs && mv README.md ../docs  # Move the runbook, readme
cp static.css ../docs/_static && touch ../docs/.nojekyll
