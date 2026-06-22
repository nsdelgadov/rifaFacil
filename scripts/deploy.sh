#!/bin/bash
# Ejecutado por GitHub Actions en cada push a main.
set -e

cd /srv/rifafacil
git pull origin main
source .venv/bin/activate
pip install -e . --quiet

VERSION=$(python -c "import tomllib; print(tomllib.load(open('pyproject.toml','rb'))['project']['version'])")
if grep -q "^APP_VERSION=" /etc/rifafacil.env; then
    sudo sed -i "s/^APP_VERSION=.*/APP_VERSION=$VERSION/" /etc/rifafacil.env
else
    echo "APP_VERSION=$VERSION" | sudo tee -a /etc/rifafacil.env > /dev/null
fi

sudo systemctl restart rifafacil
