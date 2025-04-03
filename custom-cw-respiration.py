import numpy as np
import scipy.constants
import matplotlib.pyplot as plt
from scipy.signal import butter, lfilter
import adi
import time

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

# --- CW Signal for TX ---
cw_freq = 500  # Hz CW tone for Doppler detection
t = np.arange(buffer_length) / sample_rate
cw_signal = np.exp(1j * 2 * np.pi * cw_freq * t).astype(np.complex64)

# --- LPF Helper ---


def butter_bandpass(lowcut, highcut, fs, order=4):
    nyq = 0.5 * fs
    low = lowcut / nyq
    high = highcut / nyq
    b, a = butter(order, [low, high], btype='band')
    return b, a


def apply_bandpass(data, lowcut, highcut, fs):
    b, a = butter_bandpass(lowcut, highcut, fs)
    return lfilter(b, a, data)


# --- Main Loop ---
print("Starting heart & breathing rate capture (press Ctrl+C to stop)...")

try:
    phase_buffer = []
    duration_sec = 30
    start_time = time.time()

    while time.time() - start_time < duration_sec:
        sdr.tx_destroy_buffer()     # stop TX
        time.sleep(0.01)            # allow RF frontend to settle

        # Transmit chirp pulse
        sdr.tx(cw_signal)
        time.sleep(0.005)           # small TX duration

        sdr.tx_destroy_buffer()     # stop TX again before RX
        time.sleep(0.01)

        rx = sdr.rx()
        if not np.any(rx):
            print("Warning: empty RX buffer!")
            continue

        mixed = rx * np.conj(cw_signal[:len(rx)])
        phase = np.unwrap(np.angle(mixed))
        phase_buffer.extend(phase)

        time.sleep(0.025)  # remainder of 50ms cycle

    # --- Process collected data ---
    phase_array = np.array(phase_buffer)

    # Apply bandpass filters for heart and breathing components
    breathing_signal = apply_bandpass(phase_array, 0.1, 0.7, sample_rate)
    heart_signal = apply_bandpass(phase_array, 0.8, 3.0, sample_rate)

    # --- FFT ---
    def compute_peak_freq(signal, low, high):
        N = len(signal)
        if N == 0:
            return 0.0, np.array([]), np.array([])

        window = np.hanning(N)
        spectrum = np.fft.fft(signal * window)
        freqs = np.fft.fftfreq(N, 1 / sample_rate)
        mask = (freqs > low) & (freqs < high)
        if not np.any(mask):
            return 0.0, np.array([]), np.array([])
        peak_freq = freqs[mask][np.argmax(np.abs(spectrum[mask]))]
        return peak_freq, freqs[mask], spectrum[mask]

    br_freq, br_freqs, br_spectrum = compute_peak_freq(breathing_signal, 0.1, 0.7)
    hr_freq, hr_freqs, hr_spectrum = compute_peak_freq(heart_signal, 0.8, 3.0)

    # --- Plot ---
    plt.figure(figsize=(14, 6))

    plt.subplot(2, 2, 1)
    plt.plot(breathing_signal)
    plt.title("Filtered Breathing Signal")
    plt.xlabel("Sample")
    plt.ylabel("Phase (rad)")

    plt.subplot(2, 2, 2)
    if len(br_freqs) > 0:
        plt.plot(br_freqs, 20 * np.log10(np.abs(br_spectrum)))
        plt.title(f"Breathing Rate Spectrum (Peak: {br_freq:.2f} Hz / {br_freq*60:.2f} BPM)")
    else:
        plt.title("Breathing Rate Spectrum (No valid peak)")
    plt.xlabel("Frequency (Hz)")
    plt.ylabel("Magnitude (dB)")

    plt.subplot(2, 2, 3)
    plt.plot(heart_signal)
    plt.title("Filtered Heartbeat Signal")
    plt.xlabel("Sample")
    plt.ylabel("Phase (rad)")

    plt.subplot(2, 2, 4)
    if len(hr_freqs) > 0:
        plt.plot(hr_freqs, 20 * np.log10(np.abs(hr_spectrum)))
        plt.title(f"Heart Rate Spectrum (Peak: {hr_freq:.2f} Hz / {hr_freq*60:.2f} BPM)")
    else:
        plt.title("Heart Rate Spectrum (No valid peak)")
    plt.xlabel("Frequency (Hz)")
    plt.ylabel("Magnitude (dB)")

    plt.tight_layout()
    plt.show()

except KeyboardInterrupt:
    print("Stopped by user.")

finally:
    sdr.tx_destroy_buffer()
    del sdr
