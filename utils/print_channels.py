import pyaudio

p = pyaudio.PyAudio()

print()
print('''** Set INPUT_DEVICE_INDEX in config.yaml to the system's microphone index number. **\n
Note: this index may change on system reboot and need updated. 
'''
)
print()

print(p.get_device_count())
for x in range(p.get_device_count()):
    device_info = p.get_device_info_by_index(x)
    
    print(f"For device name: {device_info['name']}")
    print(f"Set INPUT_DEVICE_INDEX to {device_info['index']}")
    
    print()