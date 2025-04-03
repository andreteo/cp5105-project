import numpy as np
import scipy.constants
import matplotlib.pyplot as plt
import adi
import time
import os
import json
import adi
import multiprocessing as mp
import math

from scipy.signal import butter, lfilter, periodogram
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

    fig, axs = plt.subplots(1, 2, figsize=(12, 4))
    time_ax, freq_ax = axs

    # Collect data
    for frame in range(num_frames):
        x = recorder.sdr.rx()

        # Plot Freq Domain
        f, Pxx_den = periodogram(x, fs)
        freq_ax.clear()
        freq_ax.semilogy(f, Pxx_den)
        freq_ax.set_xlim([-100000, 100000])
        freq_ax.set_ylim([1e-7, 1e2])
        freq_ax.set_xlabel("frequency [Hz]")
        freq_ax.set_ylabel("PSD [V**2/Hz]")
        freq_ax.set_title("Frequency Domain")
        freq_ax.grid(True)

        # Plot Time Domain
        time_ax.clear()
        time_ax.plot(x[:10000].real)  # You can also use np.abs(x) or np.imag(x)
        time_ax.set_ylim([-2**9, 2**9])
        time_ax.set_xlabel("Sample Index")
        time_ax.set_ylabel("Amplitude")
        time_ax.set_title("Time Domain")
        time_ax.grid(True)

        plt.tight_layout()
        plt.pause(0.05)

    plt.show()
