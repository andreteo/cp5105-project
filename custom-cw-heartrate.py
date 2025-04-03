import numpy as np
import scipy.constants
import matplotlib.pyplot as plt
from scipy.signal import butter, lfilter
import adi
import time
import adi
import numpy as np
import matplotlib.pyplot as plt
import scipy
from dsp import DSP

# --- SDR Configuration ---
sdr = adi.Pluto("ip:192.168.2.1")

sample_rate = int(1e6)
center_freq = int(2.4e9)
buffer_length = 4096
sdr.sample_rate = sample_rate
sdr.rx_lo = center_freq
sdr.tx_lo = center_freq
sdr.tx_hardwaregain_chan0 = -10  # adjust to avoid RX overload
sdr.rx_hardwaregain_chan0 = 40
sdr.rx_buffer_size = buffer_length
sdr.gain_control_mode_chan0 = "manual"

# --- CW Signal for TX (constant tone) ---
t = np.arange(buffer_length) / sample_rate
cw_signal = np.exp(1j * 2 * np.pi * 0 * t).astype(np.complex64)
sdr.tx_cyclic_buffer = True
sdr.tx(cw_signal)

# --- LPF Helper ---


def butter_lowpass(cutoff, fs, order=4):
    nyq = 0.5 * fs
    normal_cutoff = cutoff / nyq
    b, a = butter(order, normal_cutoff, btype='low', analog=False)
    return b, a


def apply_lowpass(data, cutoff=5.0, fs=sample_rate):
    b, a = butter_lowpass(cutoff, fs)
    return lfilter(b, a, data)


# --- Main Loop ---
print("Starting heart rate capture (press Ctrl+C to stop)...")

try:
    phase_buffer = []
    duration_sec = 20
    start_time = time.time()

    while time.time() - start_time < duration_sec:
        rx = sdr.rx()
        mixed = rx * np.conj(cw_signal[:len(rx)])
        phase = np.unwrap(np.angle(mixed))
        phase_buffer.extend(phase)

    # --- Process collected data ---
    phase_array = np.array(phase_buffer)
    phase_filtered = apply_lowpass(phase_array)

    # --- FFT ---
    N = len(phase_filtered)
    window = np.hanning(N)
    spectrum = np.fft.fft(phase_filtered * window)
    freqs = np.fft.fftfreq(N, 1 / sample_rate)

    # --- Limit to HR range ---
    mask = (freqs > 0.5) & (freqs < 3)
    peak_freq = freqs[mask][np.argmax(np.abs(spectrum[mask]))]
    bpm = peak_freq * 60

    # --- Plot ---
    plt.figure(figsize=(12, 5))
    plt.subplot(1, 2, 1)
    plt.plot(phase_filtered)
    plt.title("Filtered Phase Signal")
    plt.xlabel("Sample")
    plt.ylabel("Phase (rad)")

    plt.subplot(1, 2, 2)
    plt.plot(freqs[mask], 20 * np.log10(np.abs(spectrum[mask])))
    plt.title(f"Heart Rate Spectrum (Peak: {bpm:.2f} BPM)")
    plt.xlabel("Frequency (Hz)")
    plt.ylabel("Magnitude (dB)")
    plt.tight_layout()
    plt.show()

except KeyboardInterrupt:
    print("Stopped by user.")

finally:
    sdr.tx_destroy_buffer()
    del sdr
