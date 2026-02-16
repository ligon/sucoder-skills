#!/usr/bin/env bash
#
# Batch export an Org file to PDF using Emacs.
# Usage: ./export-pdf.sh path/to/document.org
#
# Assumes Emacs is installed and that ~/.emacs.d/init.el configures org-export.

set -euo pipefail

if [[ $# -ne 1 ]]; then
  echo "Usage: $0 path/to/document.org" >&2
  exit 1
fi

ORG_FILE="$1"

if [[ ! -f "$ORG_FILE" ]]; then
  echo "Error: $ORG_FILE not found." >&2
  exit 2
fi

emacs --batch "$ORG_FILE" \
  -l ~/.emacs.d/init.el \
  -f org-latex-export-to-pdf
