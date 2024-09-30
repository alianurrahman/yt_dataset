import shlex
from subprocess import run

import click
import yt_dlp as youtube_dl
from pydub import AudioSegment
from pydub.silence import split_on_silence
from termcolor import colored

from scripts.utility import parse_config, convert_audio


@click.command()
@click.argument("config_file", type=str, default="config.yml")
def yt_dataset(config_file):
    link_num = 1  # iterates over the links in the TXT file
    config = parse_config(config_file)

    with open(config["links_file"]) as fp:
        for link in fp:
            print("\nStarting processing for link number ", link_num)

            # Step 1: Extract and download the audio
            try:
                with youtube_dl.YoutubeDL(config["ydl_opts"]) as ydl:
                    ydl.download([link])
            except Exception as e:
                print(colored("Link number {} cannot be downloaded. Exception: {}".format(link_num, e), 'red'))
                continue  # continue with the next link in the file

            # Step 2: Separate voice from the audio
            run(shlex.split("spleeter separate -p spleeter:2stems -o output 'audio.wav'"))

            # Step 3: Adjust the sampling rate, sample width, and channels
            convert_audio("./output/audio/vocals.wav")

            # Step 4: Split into smaller parts
            sound_file = AudioSegment.from_wav("./output/audio/vocals.wav")
            audio_chunks = split_on_silence(sound_file,
                                            # must be silent for at least half a second
                                            min_silence_len=500,

                                            # consider it silent if quieter than -16 dBFS
                                            silence_thresh=-50
                                            )
            print("exporting files for link number: ", link_num)
            run(["mkdir", "{}".format(link_num)])  # making folder named after link number we are processing
            for i, chunk in enumerate(audio_chunks):
                out_file = "{0}/{0}_{1}.wav".format(link_num, i)
                chunk.export(out_file, format="wav")

            link_num += 1

            # deleting the redundant files generated for previous link to save space
            run(shlex.split("rm -rf output"))
            run(shlex.split("rm audio.wav"))


if __name__ == "__main__":
    yt_dataset()
