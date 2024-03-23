#!/bin/bash
# 'set -e' stops the execution of a script if a command or pipeline has an error.
# This is the opposite of the default shell behaviour, which is to ignore errors in scripts.
set -e

# shellcheck disable=SC2155
export ROOT="$(pwd)"  # root is mandatory, so set to pwd

clean_docs() {
  # Clean up docs directory keeping the CNAME file if present
  directory="docs"
  file_to_keep="CNAME"
  shopt -s dotglob  # enables the dotglob option, which makes the * (wildcard) include dot files (hidden files)
  cd "$directory" || return 0
  for file in *; do
      if [ "$file" != "$file_to_keep" ]; then
          rm -rf "$file"
      fi
  done
  shopt -u dotglob  # disables the dotglob option after the loop to revert to the default behavior
}

update_release_notes() {
  # Update release notes
  gitverse-release reverse -f release_notes.rst -t 'Release Notes'
}

gen_docs() {
  # Generate sphinx docs
  mkdir -p doc_gen/_static  # Create a _static directory if unavailable
  cp README.md doc_gen  # Copy readme file to doc_gen
  cd doc_gen && make clean html  # cd into doc_gen and create the runbook
  mv _build/html/* ../docs && mv README.md ../docs  # Move the runbook, readme
  cp static.css ../docs/_static
}

gen_docs &
clean_docs &
update_release_notes &

wait

# The existence of this file tells GitHub Pages not to run the published files through Jekyll.
# This is important since Jekyll will discard any files that begin with _
touch docs/.nojekyll
