# GNU Radio 3.10 Python Flow Graph Snippet (for heart/breathing phase monitoring)

from gnuradio import gr
from gnuradio import blocks, filter, analog, qtgui, iio
from gnuradio.filter import firdes
from gnuradio.qtgui import time_sink_f
from PyQt5 import Qt
import sip
import numpy as np


class PhasePlotApp(gr.top_block, Qt.QWidget):
    def __init__(self):
        gr.top_block.__init__(self, "Real-Time Phase Monitoring")
        Qt.QWidget.__init__(self)
        self.setWindowTitle("ECG-style Phase Monitor")

        # SDR params
        samp_rate = 1_000_000
        tx_freq = 2.4e9
        cw_freq = 500  # Hz
        decim_factor = 1000
        lowpass_cutoff = 5.0

        # SDR TX Signal
        t = np.arange(4096) / samp_rate
        tx_signal = np.exp(1j * 2 * np.pi * cw_freq * t).astype(np.complex64)
        self.tx_src = blocks.vector_source_c(tx_signal, True, 1, [])

        # PlutoSDR blocks
        self.pluto_tx = iio.fmcomms2_sink_fc32('ip:192.168.2.1', [True, True], 4096)
        self.pluto_tx.set_samplerate(int(samp_rate))
        self.pluto_tx.set_frequency(int(tx_freq))
        self.pluto_tx.set_attenuation(0, 10)

        self.pluto_rx = iio.fmcomms2_source_fc32('ip:192.168.2.1', [True, True], 4096)
        self.pluto_rx.set_samplerate(int(samp_rate))
        self.pluto_rx.set_frequency(int(tx_freq))
        self.pluto_rx.set_gain_mode(0, 'manual')
        self.pluto_rx.set_gain(0, 50)

        # Multiply RX * conj(TX)
        self.tx_conj = blocks.conjugate_cc()
        self.mixer = blocks.multiply_cc()

        # Phase Extract & Unwrap
        self.complex_to_arg = blocks.complex_to_arg()
        self.unwrap = blocks.unwrapped_phase_ff()

        # Decimate with LPF
        self.lpf = filter.fir_filter_fff(
            decim_factor,
            firdes.low_pass(
                1.0,
                samp_rate,
                lowpass_cutoff,
                1.0,
                firdes.WIN_HAMMING
            )
        )

        # Time sink
        self.time_sink = qtgui.time_sink_f(
            1024, samp_rate / decim_factor, "Unwrapped Phase", 1
        )
        self.time_sink.set_y_axis(-10, 10)
        self.time_win = sip.wrapinstance(self.time_sink.qwidget(), Qt.QWidget)

        # Layout
        self.layout = Qt.QVBoxLayout()
        self.setLayout(self.layout)
        self.layout.addWidget(self.time_win)

        # Connections
        self.connect(self.tx_src, self.tx_conj)
        self.connect(self.tx_src, self.pluto_tx)
        self.connect(self.pluto_rx, (self.mixer, 0))
        self.connect(self.tx_conj, (self.mixer, 1))
        self.connect(self.mixer, self.complex_to_arg)
        self.connect(self.complex_to_arg, self.unwrap)
        self.connect(self.unwrap, self.lpf)
        self.connect(self.lpf, self.time_sink)


if __name__ == '__main__':
    import sys
    app = Qt.QApplication(sys.argv)
    tb = PhasePlotApp()
    tb.start()
    tb.show()
    app.exec_()
    tb.stop()
    tb.wait()
