import numpy as np
from gnuradio import gr
import math

class mfcw_vco_control(gr.sync_block):
    """
    Generates a stepped frequency control signal (float) to drive a VCO block
    in GNU Radio. The VCO then outputs a multi-frequency waveform in time.

    The control waveform cycles from:
      f0, f0 + delta_f, ..., f0 + (N-1)*delta_f
    staying at each step for 'dwell_samples' samples,
    and repeats indefinitely.

    All frequency units here are in Hz (converted to rad/s before output).
    """

    def __init__(self, samp_rate=1e6, f0=1e5, N=5, delta_f=1e5, dwell_samples=1000):
        gr.sync_block.__init__(
            self,
            name="mfcw_vco_control",
            in_sig=None,
            out_sig=[np.float32]
        )
        self.samp_rate = float(samp_rate)
        self.f0 = float(f0)
        self.N = int(N)
        self.delta_f = float(delta_f)
        self.dwell_samples = int(dwell_samples)

        # Build the control waveform array
        # Frequencies in rad/s = 2*pi*(f0 + i*delta_f)
        self.waveform = []
        for i in range(self.N):
            freq_hz = self.f0 + i * self.delta_f
            freq_rad = 2.0 * math.pi * freq_hz
            # fill 'dwell_samples' entries with freq_rad
            self.waveform.extend([freq_rad] * self.dwell_samples)

        # Convert to numpy float32 array
        self.waveform = np.array(self.waveform, dtype=np.float32)
        self.waveform_len = len(self.waveform)

        # Pointer for indexing the waveform
        self.ptr = 0

    def work(self, input_items, output_items):
        out = output_items[0]
        out_len = len(out)
        for i in range(out_len):
            out[i] = self.waveform[self.ptr]
            self.ptr = (self.ptr + 1) % self.waveform_len
        return out_len
