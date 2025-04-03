import adi
from adi.tddn import tddn


class RecorderTDDN:
    def __init__(self, config):
        fields_to_cast = {
            'sample_rate': int,
            'center_frequency': int,
            'tx_lo': int,
            'rx_lo': int,
            'tx_hardwaregain_chan0': int,
            'rx_hardwaregain_chan0': int,
            'bw': int,
            'tx_cyclic_buffer': bool
        }

        for k, v in config.items():
            casted_value = fields_to_cast.get(k, lambda x: x)(v)
            setattr(self, k, casted_value)

        # --- PlutoSDR Configuration ---
        self.tdd = tddn(uri=self.uri)  # Initialize TDD controller

        self.sdr = adi.Pluto(self.uri)
        self.sdr.sample_rate = self.sample_rate
        self.sdr.rx_lo = self.rx_lo
        self.sdr.tx_lo = self.tx_lo
        self.sdr.tx_hardwaregain_chan0 = self.tx_hardwaregain_chan0
        self.sdr.rx_hardwaregain_chan0 = self.rx_hardwaregain_chan0
        # self.sdr.rx_buffer_size = self.buffer_length
        self.sdr.gain_control_mode_chan0 = self.gain_control_mode_chan0
        self.sdr.tx_cyclic_buffer = self.tx_cyclic_buffer
        self.sdr.rx_rf_bandwidth = self.bw


class Recorder:
    def __init__(self, config):
        fields_to_cast = {
            'sample_rate': int,
            'center_frequency': int,
            'tx_lo': int,
            'rx_lo': int,
            'tx_hardwaregain_chan0': int,
            'rx_hardwaregain_chan0': int,
            'bw': int,
            'tx_cyclic_buffer': bool
        }

        for k, v in config.items():
            casted_value = fields_to_cast.get(k, lambda x: x)(v)
            setattr(self, k, casted_value)

        # --- PlutoSDR Configuration ---
        self.sdr = adi.Pluto(self.uri)
        self.sdr.sample_rate = self.sample_rate
        self.sdr.rx_lo = self.rx_lo
        self.sdr.tx_lo = self.tx_lo
        self.sdr.tx_hardwaregain_chan0 = self.tx_hardwaregain_chan0
        self.sdr.rx_hardwaregain_chan0 = self.rx_hardwaregain_chan0
        # self.sdr.rx_buffer_size = self.buffer_length
        self.sdr.gain_control_mode_chan0 = self.gain_control_mode_chan0
        self.sdr.tx_cyclic_buffer = self.tx_cyclic_buffer
        self.sdr.rx_rf_bandwidth = self.bw
