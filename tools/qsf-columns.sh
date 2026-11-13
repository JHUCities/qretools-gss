#!/usr/bin/env bash
# Writes the Qualtrics column map of a fielded survey: maps/<instrument>-ddi-qsf.columns.json.
# Usage: tools/qsf-columns.sh <instrument> <tag>, for example tools/qsf-columns.sh gss_2010 v15.
# It runs `qretools qsf-map` on the instrument at the release tag, with the QREtools that the
# tag's own mise.toml pins: that version built the release, so it makes the same DDI. The
# release must be made with QREtools 2.0.0-alpha.12 or later. Needs git, Node and npx.
set -euo pipefail

if [[ $# -ne 2 || ! "$2" =~ ^v[1-9][0-9]*$ ]]; then
  echo "Usage: tools/qsf-columns.sh <instrument> <tag>, for example gss_2010 v15" >&2
  exit 2
fi
instrument=$1 tag=$2
cd "$(git rev-parse --show-toplevel)"

map="maps/$instrument-ddi-qsf.columns.json"
if [[ -e "$map" ]]; then
  echo "$map exists. Do not make the map of a fielded survey again." >&2
  exit 1
fi

git fetch -q origin "refs/tags/$tag:refs/tags/$tag"
version=$(git show "$tag:mise.toml" | sed -nE 's/^"npm:qretools".*version = "([^"]+)".*/\1/p')
if [[ -z "$version" ]]; then
  echo "$tag: its mise.toml pins no qretools, so it is not a release of this workspace." >&2
  exit 1
fi
repo=$(git remote get-url origin | sed -E 's#\.git$##; s#.*[:/]([^/]+/[^/]+)$#\1#')

# The site of the Pages workflow (ddi.yml), which publishes each release's DDI.
pages="$(tr '[:upper:]' '[:lower:]' <<<"${repo%%/*}").github.io/${repo#*/}"

if ! npx --yes "qretools@$version" qsf-map "$repo@$tag:$instrument" -o maps; then
  echo "If $tag was made before QREtools 2.0.0-alpha.12, its tag cannot be read. Then download" >&2
  echo "its DDI, https://$pages/$tag/instruments/$instrument.json," >&2
  echo "and run qretools qsf-map <that file> -o maps. That map does not record the release." >&2
  exit 1
fi
