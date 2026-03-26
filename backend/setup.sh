#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")"
pip install -r requirements.txt
python -m spacy download en_core_web_sm
cp -n .env.example .env || true
echo "Fill in ANTHROPIC_API_KEY in backend/.env if you want live Claude synthesis."
uvicorn app.main:app --reload
