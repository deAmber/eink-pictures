#!/bin/bash
set -e

VENV="$HOME/.virtualenvs/pimoroni"

source "$VENV/bin/activate"

exec python "$HOME/eink_pictures/show_image.py" "$@"