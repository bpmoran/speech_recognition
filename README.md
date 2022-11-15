<h1>Speech Recognition Module</h1>

This package is a speech recogition module using the vosk speech recognition toolkit. 
<br/><br/>

<h2> Getting started... </h2></br>

<h3>Prereqs </h3>
1. Have Python 3 installed<br/>
2. Have pip package manager installed <br/>
3. Have Python venv installed<br/>
4. If not already installed, download [Homebrew](https://brew.sh/). Homebrew is required for installing portaudio
<br/><br/>

<h3>Install and Configure</h3>

1. Run the install script from the command line with `source ./install.sh`.<br/>
This will start a virtual environment and install the required python packages.<br/>
2. Run print_channels.py to find your system's microphone index. Update INPUT_DEVICE_INDEX in config.yaml to the appropriate index. 
3. Download your desired Vosk model from [the vosk website](https://alphacephei.com/vosk/models) and update your config to point at the model path. 

</br>

<h2> Known issues </h2>

1. Starting and stopping recordings multiple times can lead to seg fault. 

2. On install with Macbook M1 chips: 

Error: `'portaudio.h' file not found #include "portaudio.h"`
Fix: 

A. Install `portaudio` with `brew install portaudio`

B. Link portaudio `brew link portaudio`

C. Copy the path where `portaudio` was installed for use in next step with ` brew --prefix portaudio` 

D. Create `.pydistutils.cfg` in your home directory with `sudo nano $home./pydistutils.cfg` and paste the following, including the path from step C.:

```
[build_ext]
include_dirs=<PATH FROM STEP 3>/include/
library_dirs=<PATH FROM STEP 3>/lib/

```

E. Install pyaudio with `pip install pyaudio` or `pip3 install pyaudio`.

</br>
<h4> Future work </h4>
1. Replace Pyaudio dependency with Sounddevice due to latency issues with Pyaudio. 
