# Signature: GitHub tan90xx
# Modified: 2025-12-09

import dawdreamer as daw
import numpy as np
from scipy.io import wavfile
SAMPLE_RATE = 44100
INSTRUMENT_PATH = "C:\\Program Files\\Common Files\\VST3\\Kontakt.vst3"
# EFFECT_PATH = "C:\\Program Files\\Common Files\\VST3\\Surge Synth Team\\Surge XT Effects.vst3\\Contents\\x86_64-win\\Surge XT Effects.vst3"

engine = daw.RenderEngine(SAMPLE_RATE, 512)
engine.set_bpm(120.)

synth = engine.make_plugin_processor("synth", INSTRUMENT_PATH)
# synth.open_editor()
# synth.save_state("synth_state.vststate")
synth.load_state("synth_state.vststate")


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
        
        # (MIDI note, velocity, start sec, duration sec)
        synth.load_midi(input_path)

        # optionally capture intermediate audio
        # synth.record = True

        # effect = engine.make_plugin_processor("effect", EFFECT_PATH)

        engine.load_graph([
        (synth, []),
        # (effect, [synth.get_name()])  # effect needs 2 channels, and "synth" provides those 2.
        ])


        engine.render(40.)  # render 4 seconds.
        # audio = engine.get_audio()
        # audio = audio[:2, :]  # get first two channels (synth output)
        # wavfile.write("synth_demo_wet.wav", SAMPLE_RATE, audio.T)
        synth_audio = engine.get_audio("synth")
        synth_audio = synth_audio[:2, :] 
        wavfile.write(output_path, SAMPLE_RATE, synth_audio.T)
        synth.clear_midi()

batch_convert_midi_to_wav("./midi_files", "./wav_outputs")