#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
REPO='farizzz316/regujaga-ddp1'
command -v git >/dev/null || { echo 'Git belum terpasang: https://git-scm.com/downloads'; exit 1; }
command -v gh >/dev/null || { echo 'GitHub CLI belum terpasang: https://cli.github.com/'; exit 1; }
gh auth status >/dev/null 2>&1 || gh auth login --hostname github.com --web
login="$(gh api user --jq .login)"
[[ "$login" == 'farizzz316' ]] || { echo "Akun aktif: $login; harap masuk ke farizzz316"; exit 1; }
git config user.name >/dev/null || { echo 'Atur: git config --global user.name "Nama Anda"'; exit 1; }
git config user.email >/dev/null || { echo 'Atur: git config --global user.email "email-github"'; exit 1; }
if ! git rev-parse --is-inside-work-tree >/dev/null 2>&1; then git init; fi
git add .
if ! git diff --cached --quiet; then git commit -m 'chore: initial ReguJaga MVP source code'; fi
git rev-parse --verify HEAD >/dev/null
git branch -M main
if ! gh repo view "$REPO" >/dev/null 2>&1; then
  gh repo create "$REPO" --public --description 'ReguJaga - penjadwalan relawan berbasis Python, CSP dan backtracking untuk proyek DDP1 UI' --source . --remote origin --push
else
  if ! git remote get-url origin >/dev/null 2>&1; then git remote add origin "https://github.com/$REPO.git"; fi
  [[ "$(git remote get-url origin)" == *"$REPO"* ]] || { echo 'Remote origin tidak sesuai!'; exit 1; }
  git push -u origin main
fi
gh repo view "$REPO" --json url,visibility --jq '.url + " [" + .visibility + "]"'
