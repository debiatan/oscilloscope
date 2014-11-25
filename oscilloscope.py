#!/usr/bin/env python
from __future__ import division
from __future__ import print_function

import os
import serial
import time

class Oscilloscope(object):
    def __init__(self, sampling_rate, port='', baudrate=115200):
        if port == '':
            ports = [os.path.join('/dev', f) for f in os.listdir('/dev') 
                     if 'ttyUSB' in f]
            port = ports[0]

        self.serial = serial.Serial(port, baudrate)
        self.period = 1./sampling_rate
        self.reading_no = 0
        self.last_reading = 0.

        if 'ttyUSB' in port:
            time.sleep(2)       # My arduino 2009 resets after serial connection

    def read(self):
        full_reading = False
        while not full_reading:
            first = ord(self.serial.read())
            while not first & 0b10000000:
                first = ord(self.serial.read())
                self.reading_no += 1
            parity_first = first & 0b00100000;

            second = ord(self.serial.read())
            parity_second = second & 0b00100000;
            
            if second & 0b01000000 and parity_first == parity_second:
                full_reading = True
                if bool(parity_first) != bool(self.reading_no%2):
                    self.reading_no += 1

            t = self.reading_no * self.period
            self.reading_no += 1

        return (first&0b00011111)<<5 | (second&0b00011111), t

    def close(self):
        self.serial.close()
        return True

    def __del__(self):
        self.serial.close()
