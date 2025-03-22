"""
Embedded Python Blocks:

Each time this file is saved, GRC will instantiate the first class it finds
to get ports and parameters of your block. The arguments to __init__  will
be the parameters. All of them are required to have default values!
"""

import numpy as np
from gnuradio import gr

class blk(gr.sync_block):
    def __init__(self, samp_rate=1e6, bw=100e3, duration=70e-6, total_samples=70):
        gr.sync_block.__init__(
            self,
            name="Tagged Complex FMCW Chirp",
            in_sig=None,
            out_sig=[np.complex64]
        )

        self.samp_rate = int(samp_rate)
        self.bw = bw
        self.duration = duration
        self.total_samples = int(total_samples)

        self.n_chirp = int(duration * samp_rate)
        self.n_idle = self.total_samples - self.n_chirp

        # Time vector for chirp
        t = np.arange(self.n_chirp) / self.samp_rate
        slope = (2 * self.bw) / self.duration  # Hz/s

        # Instantaneous phase: phi(t) = 2π(f0 t + ½ S t²)
        phase = 2 * np.pi * (-self.bw * t + 0.5 * slope * t**2)
        chirp = np.exp(1j * phase).astype(np.complex64)

        # Combine chirp + idle (silence)
        idle = np.zeros(self.n_idle, dtype=np.complex64)
        self.frame = np.concatenate((chirp, idle))

        self.ptr = 0
        self.abs_sample_count = 0  # Needed for tagging

    def work(self, input_items, output_items):
        out = output_items[0]
        n = len(out)

        for i in range(n):
            out[i] = self.frame[self.ptr]

            self.ptr = (self.ptr + 1) % self.total_samples
            self.abs_sample_count += 1

        return n
