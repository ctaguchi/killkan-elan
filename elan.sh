#!/bin/bash
# Set environmental variables and locale-specific settings needed for
# this recognizer to run as expected before calling the recognizer.
# Change the environment variable below to the location of the ffmpeg
# in your system.

export LC_ALL="en_US.UTF-8"
export PYTHONIOENCODING="utf-8"
export FFMPEG_DIR="/opt/homebrew/bin/ffmpeg"
export PATH="$PATH:$FFMPEG_DIR"

# Run                                                                                                                                                                                                                
source ./.venv/bin/activate
exec python elan.py
