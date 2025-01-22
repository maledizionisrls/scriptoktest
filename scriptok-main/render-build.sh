#!/bin/bash
set -eux  # Mostra eventuali errori
playwright install chromium  # Scarica Chromium
pip install -r requirements.txt  # Installa le librerie Python
