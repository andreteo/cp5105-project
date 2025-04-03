import numpy as np
from gnuradio import gr

class sum_signals(gr.sync_block):
    """
    Sums an arbitrary number of float streams.
    """
    def __init__(self, n_inputs=5):
        gr.sync_block.__init__(
            self,
            name="sum_signals",
            in_sig=[np.complex64] * n_inputs,
            out_sig=[np.complex64]
        )

    def work(self, input_items, output_items):
        # Initialize output to zero
        result = np.zeros_like(output_items[0])
        # Sum all input streams elementwise
        for sig in input_items:
            result += sig
        output_items[0][:] = result
        return len(output_items[0])
