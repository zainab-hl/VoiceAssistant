import sounddevice as sd
import numpy as np
import wavio
import os

def record_until_silence(
    filename="audio/recording.wav", #folder of recordings 
    samplerate=48000, # my microphone supports 48000Hz
    threshold=0.002,
    silence_limit=1.5, #seconds of silence before stopping
    chunk_duration=0.5,
    max_duration=30.0,
    min_duration=1.5, #min recorded duration
):
    if not os.path.exists("audio"):
        os.makedirs("audio")

    sd.default.channels = 4
    print("Using input device:", sd.query_devices(sd.default.device[0])["name"])

    audio_data = []
    silent_chunks = 0
    total_time = 0

    while total_time < max_duration:
        chunk = sd.rec(
            int(chunk_duration * samplerate),
            samplerate=samplerate,
            channels=4,
            dtype="float32"
        )
        sd.wait()
        audio_data.append(chunk)
        total_time += chunk_duration

        mean_vol = np.abs(chunk[:, 0]).mean()
        print(f"Chunk mean volume: {mean_vol:.5f}")

        if mean_vol < threshold:
            silent_chunks += 1
        else:
            silent_chunks = 0

        if silent_chunks * chunk_duration >= silence_limit and total_time >= min_duration:
            break

    audio_array = np.concatenate(audio_data, axis=0)
    audio_mono = audio_array[:, 0]
    audio_int16 = np.int16(audio_mono * 32767)
    wavio.write(filename, audio_int16, samplerate, sampwidth=2)

    print(f"Saved recording: {filename}")

    return filename
