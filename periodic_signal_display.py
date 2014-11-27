#!/usr/bin/env python

from __future__ import division
from __future__ import print_function
from oscilloscope import Oscilloscope

import signal
import sys
import numpy as np
import scipy
import scipy.stats
import pylab as pl

SAMPLING_RATE = 5000        # Hz
MIN_FREQ = 10               # Hz
N_BINS = int(round(SAMPLING_RATE/MIN_FREQ))

oscilloscope = Oscilloscope(sampling_rate=SAMPLING_RATE, port='/dev/ttyUSB0')
for i in range(N_BINS): oscilloscope.read() # Throw away some data

print('Estimating frequency...')
estimates = []
for i_estimate in range(10):
    data = [oscilloscope.read()[0] for i in range(N_BINS)]
    autocorr = np.correlate(data, data, mode='full')[len(data)-1:]
    max_pos = 0
    while autocorr[max_pos+1] < autocorr[max_pos]: max_pos += 1
    while autocorr[max_pos+1] > autocorr[max_pos]: max_pos += 1
    estimates.append(SAMPLING_RATE/max_pos)

freq = scipy.stats.mode(estimates)[0][0]
samples_per_cycle = int(round(SAMPLING_RATE/freq))
samples_per_second = int(round(SAMPLING_RATE/freq))
cycles_per_second = SAMPLING_RATE/samples_per_second

print(freq, 'Hz')

vmin, vmax = min(data[-samples_per_cycle:]), max(data[-samples_per_cycle:])
zero = (vmax-vmin)/2

screen_frame_rate = 10.     # Hz

n_blocks_per_update = int(round(cycles_per_second/screen_frame_rate))

array_data = np.zeros((n_blocks_per_update, samples_per_cycle))
pos = 0
i_plot = 0
pl.ion()
xs = np.arange(0, 1/freq, (1/freq)/samples_per_cycle)
plot = pl.plot(xs, np.zeros(samples_per_cycle), linewidth=1)[0]
pl.xlim(xs.min(), xs.max())

reading_to_volt = 5/1023.

vmin_so_far, vmax_so_far = vmin*reading_to_volt, vmax*reading_to_volt
leeway = (vmax_so_far-vmin_so_far)*0.05
pl.ylim(vmin_so_far-leeway, vmax_so_far+leeway)
pl.xlabel('time (second)')
pl.ylabel('readout (volt)')
pl.title('frequency: {} Hz'.format(freq))

def signal_handler(signal, frame):
    print('Exiting...')
    sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)

while True:
    data_next = oscilloscope.read()[0]
    data_prev = data_next
    while not data_next>zero>data_prev:
        data_prev = data_next
        data_next = oscilloscope.read()[0]

    data = [oscilloscope.read()[0] for i in range(samples_per_cycle)]
    array_data[pos] = data
    pos = (pos+1)%n_blocks_per_update
    if not pos:
        wave = array_data.mean(0) * reading_to_volt
        vmin, vmax = wave.min(), wave.max()
        plot.set_ydata(pl.array(wave))
        if vmin_so_far > vmin or vmax_so_far < vmax:
            vmin_so_far, vmax_so_far = vmin, vmax
            leeway = (vmax_so_far-vmin_so_far)*0.05
            pl.ylim(vmin_so_far-leeway, vmax_so_far+leeway)
        pl.draw()
        i_plot += 1

oscilloscope.close()

