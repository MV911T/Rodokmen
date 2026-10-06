#!/bin/bash
# Rebuilds the pages from data.js and pushes to GitHub Pages. Usage: ./publish.sh "popis změny"
set -e
cd "$(dirname "$0")"
./build.sh
git add data.js template.html index.html build.sh publish.sh README.md img
git commit -q -m "${1:-Aktualizace rodokmenu}

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>" || { echo "nothing to commit"; exit 0; }
git push -q && echo "pushed"
