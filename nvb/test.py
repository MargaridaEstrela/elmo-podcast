import sounddevice as sd
import numpy as np

def find_l8_device():
    """Find Zoom LiveTrak L-8 USB device."""
    devices = sd.query_devices()
    for idx, device in enumerate(devices):
        if "LiveTrak" in device["name"] or "L-12" in device["name"]:
            return idx, device
    return None, None

def monitor_active_channels(device_index, num_channels, blocksize=1024, threshold=0.01):
    """
    Monitor which channels are currently active (signal above threshold).
    
    :param device_index: USB input device index
    :param num_channels: number of USB channels to monitor
    :param blocksize: samples per read
    :param threshold: RMS threshold to consider channel "active"
    """
    print(f"Monitoring {num_channels} channels for activity... Press Ctrl+C to stop.\n")
    
    try:
        with sd.InputStream(device=device_index,
                            channels=num_channels,
                            samplerate=44100,
                            blocksize=blocksize,
                            dtype='float32') as stream:
            while True:
                audio_block, _ = stream.read(blocksize)
                # Calculate RMS for each channel
                rms_per_channel = np.sqrt(np.mean(audio_block**2, axis=0))
                #print(rms_per_channel)
                active_channels = [i+1 for i, rms in enumerate(rms_per_channel) if rms > threshold]
                
                if active_channels:
                    print(f"Active channels: {active_channels}", end='\r')
                else:
                    print("No channels active                 ", end='\r')
                    
    except KeyboardInterrupt:
        print("\nMonitoring stopped.")

if __name__ == "__main__":
    device_index, device_info = find_l8_device()
    if device_index is None:
        print("⚠️  Zoom LiveTrak L-12 not found. Make sure it is connected and in USB Audio I/F mode.")
    else:
        print(f"Found L-8: {device_info['name']} with {device_info['max_input_channels']} channels")
        monitor_active_channels(device_index, device_info['max_input_channels'])
