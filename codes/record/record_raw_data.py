import numpy as np
import scipy.constants
import matplotlib.pyplot as plt
import time
import os
import json
import adi
import math
import h5py
from tqdm import tqdm

from datetime import datetime
from pathlib import Path
from Recorder import Recorder


if __name__ == '__main__':
    cwd = Path(os.getcwd())

    # Configuration
    config_file = 'config_fmcw.json'

    with open(cwd / 'config' / config_file, 'r') as config_file:
        config = json.load(config_file)
        sdr_config = config['sdr_config']
        signal_config = config['signal_config']
        record_config = config['record_config']

    recorder = Recorder(config=sdr_config)

    fs = int(recorder.sdr.sample_rate)
    fc = int(recorder.center_frequency)
    ts = 1 / float(fs)

    # --- Recording Parameters ---
    duration_ms = record_config['duration_ms']
    frame_length_samples = int(duration_ms / 1000 * fs)
    recorder.sdr.rx_buffer_size = frame_length_samples
    total_duration_sec = record_config['total_duration_sec']
    total_samples = int(total_duration_sec * fs)
    num_frames = math.ceil(total_samples / frame_length_samples)

    # --- CW Signal for TX ---
    if signal_config['type'] == 'cw':
        t = np.arange(0, recorder.sdr.rx_buffer_size * ts,  ts)
        i = np.cos(2 * np.pi * t * fc) * 2 ** 11
        q = np.sin(2 * np.pi * t * fc) * 2 ** 11
        iq = 0.9 * (i + 1j * q)

    elif signal_config['type'] == 'fmcw':
        duration = recorder.sdr.rx_buffer_size / fs
        t = np.arange(0, duration, 1 / fs)
        f_start = fc - recorder.bw / 2
        f_stop = fc + recorder.bw / 2
        freq_swing = (f_stop - f_start) / duration
        phase = 2 * np.pi * (f_start * t + 0.5 * freq_swing * t**2)
        i = np.cos(phase) * 2 ** 14
        q = np.sin(phase) * 2 ** 14
        iq = 0.9 * (i + 1j * q)

    # Send data
    recorder.sdr.tx(iq)

    # Data record
    out_file = ".".join([record_config["output_file"], record_config["file_ext"]])

    with h5py.File(out_file, "w") as f:
        metadata = {
            "sample_rate": recorder.sdr.sample_rate,
            "center_frequency": recorder.center_frequency,
            "tx_lo": recorder.sdr.tx_lo,
            "rx_lo": recorder.sdr.rx_lo,
            "tx_gain": recorder.sdr.tx_hardwaregain_chan0,
            "rx_gain": recorder.sdr.rx_hardwaregain_chan0,
            "buffer_length": recorder.sdr.rx_buffer_size,
            "signal_type": signal_config["type"],
            "timestamp_start": datetime.now().strftime("%m/%d/%Y, %H:%M:%S")
        }

        for k, v in metadata.items():
            f.attrs[k] = v

        # --- Datasets for dynamic data ---
        raw_data_ds = f.create_dataset("raw_iq", shape=(num_frames, recorder.sdr.rx_buffer_size), dtype=np.complex64)
        timestamp_ds = f.create_dataset("timestamps", shape=(num_frames,), dtype=np.float64)

        print("Recording Start")

        for frame in tqdm(range(num_frames)):
            x = recorder.sdr.rx()
            ts = time.time()

            raw_data_ds[frame] = x
            timestamp_ds[frame] = ts
