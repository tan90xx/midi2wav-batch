# Signature: GitHub tan90xx
# Modified: 2025-12-04
import pyaudio
import wave
import pygame
import threading
import time

def find_virtual_cable_device(p):
    """Find a virtual audio cable device"""
    for i in range(p.get_device_count()):
        info = p.get_device_info_by_index(i)
        if "cable" in info['name'].lower() or "virtual" in info['name'].lower():
            print(f"Found virtual audio device: {info['name']} (ID: {i})")
            return i
    print("No virtual audio device found, using default output device")
    return None

def record_audio(output_filename, record_seconds, device_index=None):
    """Record audio"""
    CHUNK = 1024
    FORMAT = pyaudio.paInt16
    CHANNELS = 2
    RATE = 44100
    
    p = pyaudio.PyAudio()
    
    # If no device specified, try to find a virtual cable / stereo mix
    if device_index is None:
        device_index = find_virtual_cable_device(p)
    
    stream = p.open(format=FORMAT,
                    channels=CHANNELS,
                    rate=RATE,
                    input=True,
                    input_device_index=device_index,
                    frames_per_buffer=CHUNK)
    
    print("Recording started...")
    frames = []
    
    for i in range(0, int(RATE / CHUNK * record_seconds)):
        data = stream.read(CHUNK)
        frames.append(data)
    
    print("Recording finished")
    
    stream.stop_stream()
    stream.close()
    p.terminate()
    
    # Save as WAV
    wf = wave.open(output_filename, 'wb')
    wf.setnchannels(CHANNELS)
    wf.setsampwidth(p.get_sample_size(FORMAT))
    wf.setframerate(RATE)
    wf.writeframes(b''.join(frames))
    wf.close()

def batch_convert_midi_to_wav(midi_folder, output_folder):
    """Batch convert MIDI files to WAV"""
    import os
    
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
    
    # Play once to estimate duration (simplified)
    for midi_file in [f for f in os.listdir(midi_folder) if f.endswith('.mid')]:
        input_path = os.path.join(midi_folder, midi_file)
        output_path = os.path.join(output_folder, 
                                  os.path.splitext(midi_file)[0] + '.wav')
        
        # Estimate MIDI duration (simplified: fixed 30s or read MIDI info)
        # Ideally parse the MIDI file to get the exact duration
        duration = estimate_midi_duration(input_path) or 30
        
        # Create threads for playback and recording
        pygame.mixer.init()
        pygame.mixer.music.load(input_path)
        
        # Recording thread
        record_thread = threading.Thread(
            target=record_audio, 
            args=(output_path, duration)
        )
        record_thread.start()
        
        # Play MIDI
        time.sleep(0.1)
        pygame.mixer.music.play()
        
        # Wait
        time.sleep(duration)
        pygame.mixer.music.stop()
        record_thread.join()
        
        print(f"Converted: {midi_file}")

def estimate_midi_duration(midi_file):
    """Estimate MIDI file duration (simplified)"""
    try:
        import mido
        mid = mido.MidiFile(midi_file)
        return mid.length + 1  # Estimated length in seconds
    except:
        return None

# Usage
batch_convert_midi_to_wav("./mid", "./wav")