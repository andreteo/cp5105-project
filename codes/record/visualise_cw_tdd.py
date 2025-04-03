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
from Recorder import RecorderTDDN
from scipy.signal import butter, lfilter, periodogram

if __name__ == '__main__':
    cwd = Path(os.getcwd())

    # Configuration
    config_file = 'config.json'

    with open(cwd / 'config' / config_file, 'r') as config_file:
        config = json.load(config_file)
        sdr_config = config['sdr_config']
        signal_config = config['signal_config']
        record_config = config['record_config']

    recorder = RecorderTDDN(config=sdr_config)

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

    # --- TDD Stuff ---
    frame_length_ms = duration_ms
    recorder.tdd.startup_delay_ms = 0
    recorder.tdd.frame_length_ms = frame_length_ms
    recorder.tdd.burst_count = 0  # 0 - continuous

    # TX DMA settings
    recorder.tdd.channel[2].on_raw = 0
    recorder.tdd.channel[2].off_raw = 10
    recorder.tdd.channel[2].polarity = 0
    recorder.tdd.channel[2].enable = 1

    # RX DMA settings
    recorder.tdd.channel[1].on_raw = 0
    recorder.tdd.channel[1].off_raw = 10
    recorder.tdd.channel[1].polarity = 0
    recorder.tdd.channel[1].enable = 1

    # Start TDD engine
    recorder.tdd.sync_external = False
    recorder.tdd.enable = True

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

    # Start TDD operation via software trigger
    recorder.tdd.sync_soft = 1

    # Data record
    out_file = ".".join([record_config["output_file"], record_config["file_ext"]])

    # with h5py.File(out_file, "w") as f:
    #     metadata = {
    #         "sample_rate": recorder.sdr.sample_rate,
    #         "center_frequency": recorder.center_frequency,
    #         "tx_lo": recorder.sdr.tx_lo,
    #         "rx_lo": recorder.sdr.rx_lo,
    #         "tx_gain": recorder.sdr.tx_hardwaregain_chan0,
    #         "rx_gain": recorder.sdr.rx_hardwaregain_chan0,
    #         "buffer_length": recorder.sdr.rx_buffer_size,
    #         "signal_type": signal_config["type"],
    #         "timestamp_start": datetime.now().strftime("%m/%d/%Y, %H:%M:%S")
    #     }

    #     for k, v in metadata.items():
    #         f.attrs[k] = v

    #     # --- Datasets for dynamic data ---
    #     raw_data_ds = f.create_dataset("raw_iq", shape=(num_frames, recorder.sdr.rx_buffer_size), dtype=np.complex64)
    #     timestamp_ds = f.create_dataset("timestamps", shape=(num_frames,), dtype=np.float64)

    #     print("Recording Start")

    #     for frame in tqdm(range(num_frames)):
    #         x = recorder.sdr.rx()
    #         ts = time.time()

    #         raw_data_ds[frame] = x
    #         timestamp_ds[frame] = ts
    fig, axs = plt.subplots(1, 2, figsize=(12, 4))
    time_ax, freq_ax = axs

    for frame in tqdm(range(num_frames)):
        x = recorder.sdr.rx()

        # Plot Freq Domain
        f, Pxx_den = periodogram(x, fs)
        freq_ax.clear()
        freq_ax.semilogy(f, Pxx_den)
        freq_ax.set_xlim([-1e6, 3e6])
        freq_ax.set_ylim([1e-7, 1e2])
        freq_ax.set_xlabel("frequency [Hz]")
        freq_ax.set_ylabel("PSD [V**2/Hz]")
        freq_ax.set_title("Frequency Domain")
        freq_ax.grid(True)

        # Plot Time Domain
        time_ax.clear()
        time_ax.plot(x[:100].real)  # You can also use np.abs(x) or np.imag(x)
        time_ax.set_ylim([-2**9, 2**9])
        time_ax.set_xlabel("Sample Index")
        time_ax.set_ylabel("Amplitude")
        time_ax.set_title("Time Domain")
        time_ax.grid(True)

        plt.tight_layout()
        plt.pause(0.05)

    recorder.tdd.enable = 0

    for i in range(3):
        recorder.tdd.channel[i].on_raw = 0
        recorder.tdd.channel[i].off_raw = 0
        recorder.tdd.channel[i].enable = 0
