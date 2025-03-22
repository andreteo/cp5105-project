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
            name="FMCW Ramp with Idle (1MS/s)",
            in_sig=None,
            out_sig=[np.float32]
        )

        self.samp_rate = int(samp_rate)
        self.bw = bw
        self.duration = duration
        self.total_samples = int(total_samples)

        self.n_chirp = int(self.total_samples // 2)
        self.n_idle = int(self.total_samples - self.n_chirp)

        # Chirp ramp from -1 to 1 (control input for VCO)
        self.chirp = np.linspace(0, 1.0, self.n_chirp, dtype=np.float32)
        self.idle = np.zeros(self.n_idle, dtype=np.float32)

        self.frame = np.concatenate((self.chirp, self.idle))
        self.ptr = 0

    def work(self, input_items, output_items):
        out = output_items[0]
        
        for i in range(len(out)):
            out[i] = self.frame[self.ptr]
            self.ptr = (self.ptr + 1) % self.total_samples
        return len(out)