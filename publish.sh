#!/usr/bin/env bash
set -euo pipefail
cd -- "$(dirname -- "$0")"
command -v gh >/dev/null || { echo 'Install GitHub CLI, then run gh auth login.'; exit 1; }
gh auth status
python3 -m unittest discover -s tests -v
PYTHONPATH=src python3 -m govai_nz.demo >/dev/null
if [[ ! -d .git ]]; then
  git init -b main
  git add .
  git commit -m 'Bootstrap unofficial GovAI-NZ reference foundation'
fi
git diff --exit-code
git diff --cached --exit-code
if git remote get-url origin >/dev/null 2>&1; then
  echo 'An origin remote already exists; inspect it before publishing.'
  exit 1
fi
gh repo create govai-nz --public --source=. --remote=origin --push \
  --description 'Unofficial community reference implementation for auditable, vendor-neutral public-sector AI in New Zealand'
