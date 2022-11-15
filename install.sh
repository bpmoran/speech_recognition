#!/bin/bash

# start env
echo 'Starting virtual environment...'
python3 -m venv env
source env/bin/activate

# brew installs
echo 'Using homebrew to install portaudio...'
brew install portaudio

# pip installs
echo 'Pip installing requirements in requirements.txt...'
pip install -r requirements.txt

echo 'Finished requirements download.'