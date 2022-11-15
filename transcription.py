import json
import logging
import os
import threading
import time
import pyaudio
import yaml

from enum import Enum
from queue import Queue
from threading import Thread
from vosk import Model, KaldiRecognizer


from thread_utils import threaded_user, threaded_daemon

class STMessage(Enum):

    # recording 
    START_RECORDING = "START_RECORDING"
    STOP_RECORDING = "STOP_RECORDING"

    # transcription
    START_TRANSCRIPTION = "START_TRANSCRIPTION"
    STOP_TRANSCRIPTION = "STOP_TRANSCRIPTION"

    # listening
    START_LISTENING = "START_LISTENING"
    STOP_LISTENING = "STOP_LISTENING"


class SpeechTranscription:   

    def __init__(self, path_to_config="config.yaml", log_level=logging.DEBUG) -> None:

        # read config
        self._logger = logging.getLogger(__name__)
        self._logger.setLevel(log_level)
        self._config = self._read_config(path_to_config)

        # set audio recorder params from config
        recorder_params = self._config.get("RECORDER", dict())
        self.AUDIO_FORMAT = eval(recorder_params.get("AUDIO_FORMAT", pyaudio.paInt16)) # need eval if string rep of pyaudio type passed in config 
        self.CHANNELS = recorder_params.get("CHANNELS", 1)
        self.CHUNK = recorder_params.get("CHUNK", 1024)
        self.FRAME_RATE  = recorder_params.get("FRAME_RATE", 16000)
        self.INPUT_DEVICE_INDEX = recorder_params.get("INPUT_DEVICE_INDEX", 1)
        self.RECORD_SECONDS  = recorder_params.get("RECORD_SECONDS", 3)
        self.SAMPLE_SIZE  = recorder_params.get("SAMPLE_SIZE", 2)

        # set model params from config
        model_params = self._config.get("MODEL", dict())
        self.MODEL_NAME = model_params.get("MODEL_NAME", "vosk-model-en-us-0.22")

        # output queues
        self.recordings = Queue(60 // self.RECORD_SECONDS) # holds up to roughly one minute of recordings 
        self.transcriptions = Queue(60 // self.RECORD_SECONDS) # holds up to roughly one minute of transcriptions 

        # control queues
        self._messages = Queue()
        self._threads = list[Thread]() 

        # control
        self._run_monitor = False
        self._record_audio = False
        self._transcribe_recordings = False
        self._listen = False   

        # start monitor daemon
        self._threads.append(self._start_monitor())

        # load transcription model
        self._logger.info(f"Loading transcription model {self.MODEL_NAME}...")
        self.model = Model(model_name=self.MODEL_NAME)
        self.rec = KaldiRecognizer(self.model, self.FRAME_RATE)
        self.rec.SetWords(True)


    def _read_config(self, path_to_config) -> None:
        path_to_config = os.path.abspath(path_to_config)
        self._logger.info(f"Reading config from {path_to_config}")
        
        with open(path_to_config, "r") as config_file:
            config = yaml.safe_load(config_file)
            self._logger.debug(f"\n{json.dumps(config, indent=4)}")
            return config
    
    @threaded_user
    def _handle_message(self, msg):
        self._logger.debug(f"Handling message {msg}")
        if msg == STMessage.START_RECORDING:
            if not self._record_audio:
                self._record_audio = True
                self._threads.append(self._start_recording())
        elif msg == STMessage.STOP_RECORDING:
            self._record_audio = False
        elif msg == STMessage.START_TRANSCRIPTION:
            self._transcribe_recordings = True
            self._threads.append(self._start_transcription())
        elif msg == STMessage.STOP_TRANSCRIPTION:
            self._transcribe_recordings = False
        elif msg == STMessage.START_LISTENING:
            self._listen = True
            self._threads.append(self._start_listening())
        elif msg == STMessage.STOP_LISTENING:
            self._listen = False 
    
    @threaded_daemon
    def _start_monitor(self):

        self._run_monitor = True
        self._logger.info(f"Starting daemon message monitoring process...")
        while self._run_monitor:
            
            # clean dead threads
            #self._threads = [t for t in self._threads if t.is_alive()]

            # check messages
            if not self._messages.empty():
                message = self._messages.get()
                self._logger.info(f"Message monitor daemon handling message: {message}")
                self._handle_message(message)
                self._messages.task_done()

                
    def start_recording(self):
        self._messages.put((STMessage.START_RECORDING))
    
    def stop_recording(self):
        self._messages.put((STMessage.STOP_RECORDING))
    
    @threaded_user
    def _start_recording(self):
        
        p = pyaudio.PyAudio()
    
        stream = p.open(format=self.AUDIO_FORMAT,
                        channels=self.CHANNELS,
                        rate=self.FRAME_RATE,
                        input=True,
                        input_device_index=self.INPUT_DEVICE_INDEX,
                        frames_per_buffer=self.CHUNK)

        frames = []

        while self._record_audio:
            data = stream.read(self.CHUNK)
            frames.append(data)
            if len(frames) >= (self.FRAME_RATE * self.RECORD_SECONDS) / self.CHUNK:
                self.recordings.put(frames.copy())
                frames = []
        self._logger.debug("okay, stopping recording...")
        stream.stop_stream()
        stream.close()
        p.terminate()

    def start_transcription(self):
        self._messages.put(STMessage.START_TRANSCRIPTION)
    
    def stop_transcription(self):
        self._messages.put(STMessage.STOP_TRANSCRIPTION)

    def get_transcription(self):
        if not self.transcriptions.empty():
            return self.transcriptions.get()
        self._logger.debug("get_transcription called on empty transcription queue.")
        return -1
    
    def start_listening(self):
        self._messages.put(STMessage.START_LISTENING)

    def stop_listening(self):
        self._messages.put(STMessage.STOP_LISTENING)
    
    @threaded_user
    def _start_listening(self):
        while self._listen:
            if not self.transcriptions.empty():
                lock = threading.Lock()
                lock.acquire()
                print(self.transcriptions.get())
                lock.release()
            time.sleep(self.RECORD_SECONDS)

    @threaded_user
    def _start_transcription(self):

        while self._transcribe_recordings:
            frames = self.recordings.get()
            self.rec.AcceptWaveform(b''.join(frames))
            result = self.rec.Result()
            text = json.loads(result)["text"]
            self.transcriptions.put(text)
            self.transcriptions.task_done()
            time.sleep(self.RECORD_SECONDS)

    
        
