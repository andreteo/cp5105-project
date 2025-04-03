import numpy as np
from gnuradio import gr

def generate_ofdm_symbol(fft_len, cp_len):
    """
    Generate a single OFDM symbol using a fixed coherent BPSK sequence.
    The subcarriers alternate between 1 and -1.
    """
    # Create a fixed coherent sequence: alternating 1 and -1 for BPSK.
    # Ensure the sequence is of length fft_len.
    coherent_seq = np.array([1 if i % 2 == 0 else -1 for i in range(fft_len)], dtype=np.complex64)
    
    # Compute the IFFT. (Scaling by fft_len here is one convention; adjust as needed.)
    ofdm_time = np.fft.ifft(coherent_seq) * fft_len
    
    # Add cyclic prefix by taking the last cp_len samples and prepending them.
    ofdm_symbol = np.concatenate((ofdm_time[-cp_len:], ofdm_time))
    
    # Return as complex64
    return ofdm_symbol.astype(np.complex64)

class coherent_ofdm_source(gr.sync_block):
    """
    Coherent OFDM Source Block

    This block continuously outputs OFDM symbols generated using a fixed coherent (pilot) sequence.
    It outputs a repeating symbol (OFDM symbol with cyclic prefix) so that the transmitted waveform is fully known.
    
    Parameters:
      fft_len : FFT length (number of subcarriers)
      cp_len  : Length of cyclic prefix
    """
    def __init__(self, fft_len=64, cp_len=16):
        gr.sync_block.__init__(
            self,
            name="OFDM Source",
            in_sig=None,
            out_sig=[np.complex64]
        )
        self.fft_len = int(fft_len)
        self.cp_len = int(cp_len)
        # Generate a single OFDM symbol with a coherent (fixed) sequence.
        self.ofdm_symbol = generate_ofdm_symbol(self.fft_len, self.cp_len)
        self.symbol_len = len(self.ofdm_symbol)
        self.ptr = 0  # Pointer to track our position within the OFDM symbol.

    def work(self, input_items, output_items):
        out = output_items[0]
        noutput = len(out)
        
        # Fill the output buffer by repeatedly copying the OFDM symbol.
        for i in range(noutput):
            out[i] = self.ofdm_symbol[self.ptr]
            self.ptr = (self.ptr + 1) % self.symbol_len  # Wrap around after one full symbol.
        
        return noutput
