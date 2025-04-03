import numpy as np
from gnuradio import gr

class blk(gr.sync_block):
    def __init__(self):
        gr.sync_block.__init__(self, name="Unwrap Phase", in_sig=[np.complex64], out_sig=[np.float32])
        self.last_angle = 0.0

    def work(self, input_items, output_items):
        phase = np.unwrap(np.angle(input_items[0]))
        output_items[0][:] = phase
        return len(output_items[0])
