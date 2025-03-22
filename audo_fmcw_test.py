#!/usr/bin/env python3
# -*- coding: utf-8 -*-

#
# SPDX-License-Identifier: GPL-3.0
#
# GNU Radio Python Flow Graph
# Title: Not titled yet
# Author: atsy_
# GNU Radio version: 3.10.10.0

from PyQt5 import Qt
from gnuradio import qtgui
from PyQt5 import QtCore
from gnuradio import blocks
from gnuradio import filter
from gnuradio.filter import firdes
from gnuradio import gr
from gnuradio.fft import window
import sys
import signal
from PyQt5 import Qt
from argparse import ArgumentParser
from gnuradio.eng_arg import eng_float, intx
from gnuradio import eng_notation
import audo_fmcw_test_epy_block_0 as epy_block_0  # embedded python block
import math
import sip



class audo_fmcw_test(gr.top_block, Qt.QWidget):

    def __init__(self):
        gr.top_block.__init__(self, "Not titled yet", catch_exceptions=True)
        Qt.QWidget.__init__(self)
        self.setWindowTitle("Not titled yet")
        qtgui.util.check_set_qss()
        try:
            self.setWindowIcon(Qt.QIcon.fromTheme('gnuradio-grc'))
        except BaseException as exc:
            print(f"Qt GUI: Could not set Icon: {str(exc)}", file=sys.stderr)
        self.top_scroll_layout = Qt.QVBoxLayout()
        self.setLayout(self.top_scroll_layout)
        self.top_scroll = Qt.QScrollArea()
        self.top_scroll.setFrameStyle(Qt.QFrame.NoFrame)
        self.top_scroll_layout.addWidget(self.top_scroll)
        self.top_scroll.setWidgetResizable(True)
        self.top_widget = Qt.QWidget()
        self.top_scroll.setWidget(self.top_widget)
        self.top_layout = Qt.QVBoxLayout(self.top_widget)
        self.top_grid_layout = Qt.QGridLayout()
        self.top_layout.addLayout(self.top_grid_layout)

        self.settings = Qt.QSettings("GNU Radio", "audo_fmcw_test")

        try:
            geometry = self.settings.value("geometry")
            if geometry:
                self.restoreGeometry(geometry)
        except BaseException as exc:
            print(f"Qt GUI: Could not restore geometry: {str(exc)}", file=sys.stderr)

        ##################################################
        # Variables
        ##################################################
        self.pi = pi = math.pi
        self.bw = bw = 100e3
        self.vco_sensitivity = vco_sensitivity = 2*bw*pi
        self.tx_row = tx_row = 0
        self.tx_attenuation = tx_attenuation = 10
        self.samp_rate = samp_rate = 1e6
        self.rx_row = rx_row = 2
        self.rx_gain = rx_gain = 40
        self.lpf_row = lpf_row = 4
        self.freq = freq = 1e3
        self.duration = duration = 0.001
        self.delta_r = delta_r = 3e8/(2*bw)
        self.buffer_size = buffer_size = 1024
        self.band_rej_row = band_rej_row = 5
        self.audio_samp_rate = audio_samp_rate = 48000
        self.audio_gain = audio_gain = 50

        ##################################################
        # Blocks
        ##################################################

        self._tx_attenuation_range = qtgui.Range(0, 70, 1, 10, 200)
        self._tx_attenuation_win = qtgui.RangeWidget(self._tx_attenuation_range, self.set_tx_attenuation, "'tx_attenuation'", "counter_slider", float, QtCore.Qt.Horizontal)
        self.top_grid_layout.addWidget(self._tx_attenuation_win, 0, 0, 1, 1)
        for r in range(0, 1):
            self.top_grid_layout.setRowStretch(r, 1)
        for c in range(0, 1):
            self.top_grid_layout.setColumnStretch(c, 1)
        self._rx_gain_range = qtgui.Range(0, 70, 1, 40, 200)
        self._rx_gain_win = qtgui.RangeWidget(self._rx_gain_range, self.set_rx_gain, "'rx_gain'", "counter_slider", float, QtCore.Qt.Horizontal)
        self.top_grid_layout.addWidget(self._rx_gain_win, 2, 0, 1, 1)
        for r in range(2, 3):
            self.top_grid_layout.setRowStretch(r, 1)
        for c in range(0, 1):
            self.top_grid_layout.setColumnStretch(c, 1)
        self.qtgui_time_sink_x_5 = qtgui.time_sink_c(
            (1024*4), #size
            samp_rate, #samp_rate
            "", #name
            1, #number of inputs
            None # parent
        )
        self.qtgui_time_sink_x_5.set_update_time(0.10)
        self.qtgui_time_sink_x_5.set_y_axis(-1, 1)

        self.qtgui_time_sink_x_5.set_y_label('Amplitude', "")

        self.qtgui_time_sink_x_5.enable_tags(True)
        self.qtgui_time_sink_x_5.set_trigger_mode(qtgui.TRIG_MODE_FREE, qtgui.TRIG_SLOPE_POS, 0.0, 0, 0, "")
        self.qtgui_time_sink_x_5.enable_autoscale(False)
        self.qtgui_time_sink_x_5.enable_grid(False)
        self.qtgui_time_sink_x_5.enable_axis_labels(True)
        self.qtgui_time_sink_x_5.enable_control_panel(False)
        self.qtgui_time_sink_x_5.enable_stem_plot(False)


        labels = ['Signal 1', 'Signal 2', 'Signal 3', 'Signal 4', 'Signal 5',
            'Signal 6', 'Signal 7', 'Signal 8', 'Signal 9', 'Signal 10']
        widths = [1, 1, 1, 1, 1,
            1, 1, 1, 1, 1]
        colors = ['blue', 'red', 'green', 'black', 'cyan',
            'magenta', 'yellow', 'dark red', 'dark green', 'dark blue']
        alphas = [1.0, 1.0, 1.0, 1.0, 1.0,
            1.0, 1.0, 1.0, 1.0, 1.0]
        styles = [1, 1, 1, 1, 1,
            1, 1, 1, 1, 1]
        markers = [-1, -1, -1, -1, -1,
            -1, -1, -1, -1, -1]


        for i in range(2):
            if len(labels[i]) == 0:
                if (i % 2 == 0):
                    self.qtgui_time_sink_x_5.set_line_label(i, "Re{{Data {0}}}".format(i/2))
                else:
                    self.qtgui_time_sink_x_5.set_line_label(i, "Im{{Data {0}}}".format(i/2))
            else:
                self.qtgui_time_sink_x_5.set_line_label(i, labels[i])
            self.qtgui_time_sink_x_5.set_line_width(i, widths[i])
            self.qtgui_time_sink_x_5.set_line_color(i, colors[i])
            self.qtgui_time_sink_x_5.set_line_style(i, styles[i])
            self.qtgui_time_sink_x_5.set_line_marker(i, markers[i])
            self.qtgui_time_sink_x_5.set_line_alpha(i, alphas[i])

        self._qtgui_time_sink_x_5_win = sip.wrapinstance(self.qtgui_time_sink_x_5.qwidget(), Qt.QWidget)
        self.top_layout.addWidget(self._qtgui_time_sink_x_5_win)
        self.qtgui_time_sink_x_4 = qtgui.time_sink_f(
            (1024*4), #size
            samp_rate, #samp_rate
            "", #name
            1, #number of inputs
            None # parent
        )
        self.qtgui_time_sink_x_4.set_update_time(0.10)
        self.qtgui_time_sink_x_4.set_y_axis(-1, 1)

        self.qtgui_time_sink_x_4.set_y_label('Amplitude', "")

        self.qtgui_time_sink_x_4.enable_tags(True)
        self.qtgui_time_sink_x_4.set_trigger_mode(qtgui.TRIG_MODE_FREE, qtgui.TRIG_SLOPE_POS, 0.0, 0, 0, "")
        self.qtgui_time_sink_x_4.enable_autoscale(False)
        self.qtgui_time_sink_x_4.enable_grid(False)
        self.qtgui_time_sink_x_4.enable_axis_labels(True)
        self.qtgui_time_sink_x_4.enable_control_panel(False)
        self.qtgui_time_sink_x_4.enable_stem_plot(False)


        labels = ['Signal 1', 'Signal 2', 'Signal 3', 'Signal 4', 'Signal 5',
            'Signal 6', 'Signal 7', 'Signal 8', 'Signal 9', 'Signal 10']
        widths = [1, 1, 1, 1, 1,
            1, 1, 1, 1, 1]
        colors = ['blue', 'red', 'green', 'black', 'cyan',
            'magenta', 'yellow', 'dark red', 'dark green', 'dark blue']
        alphas = [1.0, 1.0, 1.0, 1.0, 1.0,
            1.0, 1.0, 1.0, 1.0, 1.0]
        styles = [1, 1, 1, 1, 1,
            1, 1, 1, 1, 1]
        markers = [-1, -1, -1, -1, -1,
            -1, -1, -1, -1, -1]


        for i in range(1):
            if len(labels[i]) == 0:
                self.qtgui_time_sink_x_4.set_line_label(i, "Data {0}".format(i))
            else:
                self.qtgui_time_sink_x_4.set_line_label(i, labels[i])
            self.qtgui_time_sink_x_4.set_line_width(i, widths[i])
            self.qtgui_time_sink_x_4.set_line_color(i, colors[i])
            self.qtgui_time_sink_x_4.set_line_style(i, styles[i])
            self.qtgui_time_sink_x_4.set_line_marker(i, markers[i])
            self.qtgui_time_sink_x_4.set_line_alpha(i, alphas[i])

        self._qtgui_time_sink_x_4_win = sip.wrapinstance(self.qtgui_time_sink_x_4.qwidget(), Qt.QWidget)
        self.top_layout.addWidget(self._qtgui_time_sink_x_4_win)
        self.qtgui_freq_sink_x_4 = qtgui.freq_sink_c(
            4096, #size
            window.WIN_BLACKMAN_hARRIS, #wintype
            0, #fc
            samp_rate, #bw
            "", #name
            1,
            None # parent
        )
        self.qtgui_freq_sink_x_4.set_update_time(0.10)
        self.qtgui_freq_sink_x_4.set_y_axis((-140), 10)
        self.qtgui_freq_sink_x_4.set_y_label('Relative Gain', 'dB')
        self.qtgui_freq_sink_x_4.set_trigger_mode(qtgui.TRIG_MODE_FREE, 0.0, 0, "")
        self.qtgui_freq_sink_x_4.enable_autoscale(False)
        self.qtgui_freq_sink_x_4.enable_grid(False)
        self.qtgui_freq_sink_x_4.set_fft_average(1.0)
        self.qtgui_freq_sink_x_4.enable_axis_labels(True)
        self.qtgui_freq_sink_x_4.enable_control_panel(False)
        self.qtgui_freq_sink_x_4.set_fft_window_normalized(True)



        labels = ['', '', '', '', '',
            '', '', '', '', '']
        widths = [1, 1, 1, 1, 1,
            1, 1, 1, 1, 1]
        colors = ["blue", "red", "green", "black", "cyan",
            "magenta", "yellow", "dark red", "dark green", "dark blue"]
        alphas = [1.0, 1.0, 1.0, 1.0, 1.0,
            1.0, 1.0, 1.0, 1.0, 1.0]

        for i in range(1):
            if len(labels[i]) == 0:
                self.qtgui_freq_sink_x_4.set_line_label(i, "Data {0}".format(i))
            else:
                self.qtgui_freq_sink_x_4.set_line_label(i, labels[i])
            self.qtgui_freq_sink_x_4.set_line_width(i, widths[i])
            self.qtgui_freq_sink_x_4.set_line_color(i, colors[i])
            self.qtgui_freq_sink_x_4.set_line_alpha(i, alphas[i])

        self._qtgui_freq_sink_x_4_win = sip.wrapinstance(self.qtgui_freq_sink_x_4.qwidget(), Qt.QWidget)
        self.top_layout.addWidget(self._qtgui_freq_sink_x_4_win)
        self.low_pass_filter_1 = filter.fir_filter_ccf(
            1,
            firdes.low_pass(
                1,
                samp_rate,
                120e3,
                20e3,
                window.WIN_HAMMING,
                6.76))
        self.epy_block_0 = epy_block_0.blk(samp_rate=samp_rate, bw=bw, duration=duration, total_samples=samp_rate * duration)
        self.blocks_vco_c_1 = blocks.vco_c(samp_rate, vco_sensitivity, 1)
        self.blocks_throttle2_0 = blocks.throttle( gr.sizeof_gr_complex*1, samp_rate, True, 0 if "auto" == "auto" else max( int(float(0.1) * samp_rate) if "auto" == "time" else int(0.1), 1) )
        self._audio_gain_range = qtgui.Range(0, 100, 1, 50, 200)
        self._audio_gain_win = qtgui.RangeWidget(self._audio_gain_range, self.set_audio_gain, "'audio_gain'", "counter_slider", float, QtCore.Qt.Horizontal)
        self.top_grid_layout.addWidget(self._audio_gain_win, 5, 0, 1, 1)
        for r in range(5, 6):
            self.top_grid_layout.setRowStretch(r, 1)
        for c in range(0, 1):
            self.top_grid_layout.setColumnStretch(c, 1)


        ##################################################
        # Connections
        ##################################################
        self.connect((self.blocks_throttle2_0, 0), (self.low_pass_filter_1, 0))
        self.connect((self.blocks_vco_c_1, 0), (self.blocks_throttle2_0, 0))
        self.connect((self.epy_block_0, 0), (self.blocks_vco_c_1, 0))
        self.connect((self.epy_block_0, 0), (self.qtgui_time_sink_x_4, 0))
        self.connect((self.low_pass_filter_1, 0), (self.qtgui_freq_sink_x_4, 0))
        self.connect((self.low_pass_filter_1, 0), (self.qtgui_time_sink_x_5, 0))


    def closeEvent(self, event):
        self.settings = Qt.QSettings("GNU Radio", "audo_fmcw_test")
        self.settings.setValue("geometry", self.saveGeometry())
        self.stop()
        self.wait()

        event.accept()

    def get_pi(self):
        return self.pi

    def set_pi(self, pi):
        self.pi = pi
        self.set_vco_sensitivity(2*self.bw*self.pi)

    def get_bw(self):
        return self.bw

    def set_bw(self, bw):
        self.bw = bw
        self.set_delta_r(3e8/(2*self.bw))
        self.set_vco_sensitivity(2*self.bw*self.pi)
        self.epy_block_0.bw = self.bw

    def get_vco_sensitivity(self):
        return self.vco_sensitivity

    def set_vco_sensitivity(self, vco_sensitivity):
        self.vco_sensitivity = vco_sensitivity

    def get_tx_row(self):
        return self.tx_row

    def set_tx_row(self, tx_row):
        self.tx_row = tx_row

    def get_tx_attenuation(self):
        return self.tx_attenuation

    def set_tx_attenuation(self, tx_attenuation):
        self.tx_attenuation = tx_attenuation

    def get_samp_rate(self):
        return self.samp_rate

    def set_samp_rate(self, samp_rate):
        self.samp_rate = samp_rate
        self.blocks_throttle2_0.set_sample_rate(self.samp_rate)
        self.epy_block_0.samp_rate = self.samp_rate
        self.epy_block_0.total_samples = self.samp_rate * self.duration
        self.low_pass_filter_1.set_taps(firdes.low_pass(1, self.samp_rate, 120e3, 20e3, window.WIN_HAMMING, 6.76))
        self.qtgui_freq_sink_x_4.set_frequency_range(0, self.samp_rate)
        self.qtgui_time_sink_x_4.set_samp_rate(self.samp_rate)
        self.qtgui_time_sink_x_5.set_samp_rate(self.samp_rate)

    def get_rx_row(self):
        return self.rx_row

    def set_rx_row(self, rx_row):
        self.rx_row = rx_row

    def get_rx_gain(self):
        return self.rx_gain

    def set_rx_gain(self, rx_gain):
        self.rx_gain = rx_gain

    def get_lpf_row(self):
        return self.lpf_row

    def set_lpf_row(self, lpf_row):
        self.lpf_row = lpf_row

    def get_freq(self):
        return self.freq

    def set_freq(self, freq):
        self.freq = freq

    def get_duration(self):
        return self.duration

    def set_duration(self, duration):
        self.duration = duration
        self.epy_block_0.duration = self.duration
        self.epy_block_0.total_samples = self.samp_rate * self.duration

    def get_delta_r(self):
        return self.delta_r

    def set_delta_r(self, delta_r):
        self.delta_r = delta_r

    def get_buffer_size(self):
        return self.buffer_size

    def set_buffer_size(self, buffer_size):
        self.buffer_size = buffer_size

    def get_band_rej_row(self):
        return self.band_rej_row

    def set_band_rej_row(self, band_rej_row):
        self.band_rej_row = band_rej_row

    def get_audio_samp_rate(self):
        return self.audio_samp_rate

    def set_audio_samp_rate(self, audio_samp_rate):
        self.audio_samp_rate = audio_samp_rate

    def get_audio_gain(self):
        return self.audio_gain

    def set_audio_gain(self, audio_gain):
        self.audio_gain = audio_gain




def main(top_block_cls=audo_fmcw_test, options=None):

    qapp = Qt.QApplication(sys.argv)

    tb = top_block_cls()

    tb.start()

    tb.show()

    def sig_handler(sig=None, frame=None):
        tb.stop()
        tb.wait()

        Qt.QApplication.quit()

    signal.signal(signal.SIGINT, sig_handler)
    signal.signal(signal.SIGTERM, sig_handler)

    timer = Qt.QTimer()
    timer.start(500)
    timer.timeout.connect(lambda: None)

    qapp.exec_()

if __name__ == '__main__':
    main()
