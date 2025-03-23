"""
Embedded Python Blocks:

Each time this file is saved, GRC will instantiate the first class it finds
to get ports and parameters of your block. The arguments to __init__  will
be the parameters. All of them are required to have default values!
"""

import numpy as np
from gnuradio import gr

class fmcw_ramp_gate(gr.sync_block):
    """
    Gating block for FMCW ramp:
    Passes samples only during the "up ramp" portion, zeros out everything else.
    """
    def __init__(self, total_samples=70, duty_cycle=0.7):
        gr.sync_block.__init__(
            self,
            name="FMCW Ramp Gate",
            in_sig=[np.complex64],     # or [np.complex64] if gating complex signals
            out_sig=[np.complex64]
        )
        self.total_samples = int(total_samples)
        self.duty_cycle = duty_cycle
        self.n_chirp = int(self.total_samples * self.duty_cycle)
        self.ptr = 0

    def work(self, input_items, output_items):
        in0 = input_items[0]
        out0 = output_items[0]

        for i in range(len(in0)):
            # If pointer is within the up-ramp region, pass the sample
            # Otherwise set output to 0
            if self.ptr < self.n_chirp:
                out0[i] = in0[i]
            else:
                out0[i] = 0.0

            # Increment ptr and wrap around
            self.ptr = (self.ptr + 1) % self.total_samples

        return len(out0)
