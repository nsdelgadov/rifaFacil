#!/bin/bash
# Ejecutado por GitHub Actions en cada push a main.
set -e

cd /srv/rifafacil
git pull origin main
source .venv/bin/activate
pip install -e . --quiet
sudo systemctl restart rifafacil
