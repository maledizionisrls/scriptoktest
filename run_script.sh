#!/bin/bash

# Percorso dello script
cd /opt/tiktok-scraper/code

# Attiva l'ambiente virtuale
source ../venv/bin/activate

# Esegui lo script Python
python run.py

# Disattiva l'ambiente virtuale
deactivate
