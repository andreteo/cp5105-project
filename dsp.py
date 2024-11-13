import numpy as np
import scipy
import scipy.signal


class DSP:
    def __init__(self, num_samples) -> None:
        self.num_samples = num_samples
        self.range_fft_window = np.array([scipy.signal.windows.blackman(self.num_samples)])

    def calc_range_fft(self, rx_data):
        """
        Calculate the range FFT for a single Rx channel.
        :param rx_data: 1D array of received samples from the single channel.
        :return: Range FFT array.
        """
        rx_data_nodc = rx_data - np.mean(rx_data)  # Mean removal to eliminate DC offset
        rx_data_windowed = rx_data_nodc * self.range_fft_window  # Apply window function
        rx_data_range = np.fft.fftshift(np.fft.fft(rx_data_windowed))  # Range FFT
        rx_data_range = np.abs(rx_data_range).squeeze()  # Magnitude of FFT result
        return rx_data_range
