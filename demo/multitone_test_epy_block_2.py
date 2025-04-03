import numpy as np
from gnuradio import gr
from gnuradio.filter import firdes, window

class filter_bank_vectorized(gr.sync_block):
    """
    Vectorized Filter Bank Block for Multi-Tone Extraction

    This block takes a scalar stream of complex samples as input and outputs
    one complex stream per tone. Each output is produced by applying a narrow
    bandpass filter (designed via firdes.band_pass) centered at the specified
    tone frequency. The filtering is implemented in a vectorized manner over
    a block of input samples.

    Parameters:
      samp_rate   : The sample rate of the input signal.
      tone_centers: A list of center frequencies for each tone (in Hz).
      bw          : The passband bandwidth for each filter (in Hz), e.g., 500.
      transition  : The transition width for the filters (in Hz), e.g., 100.
      beta        : The beta parameter for the window (default 6.76).
    """
    def __init__(self, samp_rate=1e6, tone_centers=[1e3, 3e3, 5e3, 7e3, 9e3], bw=1e3, transition=100, beta=6.76):
        # One output stream per tone
        out_sig = [np.complex64] * len(tone_centers)
        in_sig = [np.complex64]  # input is a stream of complex samples
        gr.sync_block.__init__(self,
            name="filter_bank_vectorized",
            in_sig=in_sig,
            out_sig=out_sig)

        self.samp_rate = samp_rate
        self.tone_centers = tone_centers
        self.bw = bw
        self.transition = transition
        self.beta = beta
        self.n_filters = len(tone_centers)
        
        # For each tone, design the filter taps and initialize a buffer for FIR filtering.
        self.filters = []  # list of numpy arrays (taps) for each filter
        self.buffers = []  # list of buffers (each of length L-1) per filter
        for f_center in tone_centers:
            taps = firdes.band_pass(
                gain=1,
                sampling_freq=samp_rate,
                low_cutoff_freq=f_center - bw/2,
                high_cutoff_freq=f_center + bw/2,
                transition_width=transition,
                window=window.WIN_HAMMING,
                param=beta  # use 'param' instead of 'beta'
            )
            taps = np.array(taps, dtype=np.complex64)
            self.filters.append(taps)
            # Initialize a buffer with length (len(taps)-1) to store previous samples.
            self.buffers.append(np.zeros(len(taps) - 1, dtype=np.complex64))

    def work(self, input_items, output_items):
        in0 = input_items[0]   # shape: (n_samples,)
        n = len(in0)
        
        # Process each filter in the bank
        for i in range(self.n_filters):
            taps = self.filters[i]
            L = len(taps)
            # Concatenate the previous buffer with the current block.
            # The padded array has length = (L-1 + n)
            pad = np.concatenate((self.buffers[i], in0))
            # Use vectorized convolution (with mode='valid') to compute outputs for this block.
            # We reverse the taps to match our desired dot product:
            #   output[k] = sum_{j=0}^{L-1} taps[j] * pad[k + L - 1 - j]
            conv_result = np.convolve(pad, taps[::-1], mode='valid')
            # conv_result will have length = n
            output_items[i][:] = conv_result
            # Update the buffer with the last (L-1) samples of pad.
            self.buffers[i] = pad[-(L - 1):].copy()
        
        return n
