#!/usr/bin/env bash
if [ ! -d "venv" ]; then
  python3 -m venv venv
fi
source venv/bin/activate
pip install --upgrade -r requirements.txt
