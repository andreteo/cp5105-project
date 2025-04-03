import numpy as np
from gnuradio import gr
import pmt

class blk(gr.sync_block):
    def __init__(self, samp_rate=1e6, bw=100e3, chirp_duration=50e-6, idle_duration=500e-6):
        gr.sync_block.__init__(
            self,
            name="FMCW Pulse Triggered",
            in_sig=None,
            out_sig=[np.float32]
        )
        
        self.samp_rate = int(samp_rate)
        self.bw = bw
        self.chirp_samples = int(chirp_duration * self.samp_rate)
        self.idle_samples = int(idle_duration * self.samp_rate)
        self.total_samples = self.chirp_samples + self.idle_samples

        self.chirp = np.linspace(0.0, 1.0, self.chirp_samples, dtype=np.float32)
        self.idle = np.zeros(self.idle_samples, dtype=np.float32)
        self.pulse = np.concatenate((self.chirp, self.idle))

        self.send_pulse = False
        self.ptr = 0

        # Register message input
        self.message_port_register_in(pmt.intern("trigger"))
        self.set_msg_handler(pmt.intern("trigger"), self.trigger_pulse)

    def trigger_pulse(self, msg):
        self.send_pulse = True
        self.ptr = 0

    def work(self, input_items, output_items):
        out = output_items[0]
        n = len(out)

        if self.send_pulse:
            remaining = self.total_samples - self.ptr
            to_copy = min(n, remaining)
            out[:to_copy] = self.pulse[self.ptr:self.ptr + to_copy]

            if to_copy < n:
                out[to_copy:] = 0.0

            self.ptr += to_copy
            if self.ptr >= self.total_samples:
                self.send_pulse = False
        else:
            out[:] = 0.0

        return len(out)
