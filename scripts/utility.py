from __future__ import unicode_literals

import yaml
from pydub import AudioSegment


def parse_config(config_file):
    with open(config_file, "rb") as f:
        config = yaml.safe_load(f)
    return config


def convert_audio(audio_file):
    """
    Corrects the channels, sample rate, and sample width of the audios.
    Replaces the original audio file with the one generated.
    """
    sound = AudioSegment.from_file(audio_file)
    sound = sound.set_frame_rate(16000)
    sound = sound.set_channels(1)
    sound = sound.set_sample_width(2)  # 2 corresponds to 16-bit sample width in Pydub
    sound.export(audio_file, format="wav")
