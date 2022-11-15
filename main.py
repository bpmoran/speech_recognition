import os
import logging
import threading
from transcription import SpeechTranscription
from time import sleep

CONFIG_PATH = "config.yaml"
CONFIG_PATH = os.path.abspath(CONFIG_PATH)

logging.basicConfig(level=logging.DEBUG)

transcriber = SpeechTranscription(path_to_config=CONFIG_PATH, log_level=logging.INFO)

# start and stop recordings
transcriber.start_recording() 
# transcriber.stop_recording() 

## start and stop transcripiton of recordings in audio queue
transcriber.start_transcription() 
# transcriber.stop_transcription()

## start and stop writing transcriptions to STDOUT with stdlib print
transcriber.start_listening() 
# transcriber.stop_listening()

usr = ''
while usr != 'q':
    usr = input('Say something or press q to quit')

    if usr == 'q':
        transcriber.stop_recording()
        transcriber.stop_transcription()
        transcriber.stop_listening()
