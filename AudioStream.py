import numpy as np
import pyaudio
import matplotlib.pyplot as plt
import struct
import sys
import time


class AudioStream(object):
    def __init__(self, rate):
        # stream constants
        self.CHUNK = 2048
        self.FORMAT = pyaudio.paFloat32
        self.CHANNELS = 1
        self.RATE = rate
        self.pause = False

        # stream object
        self.pyaudio = pyaudio.PyAudio()
        self.stream = self.pyaudio.open(
            format=self.FORMAT,
            channels=self.CHANNELS,
            rate=self.RATE,
            input=True,
            output=True,
            frames_per_buffer=self.CHUNK,
        )

    def read(self, number_of_blocks):
        result = b''

        for i in range(number_of_blocks):
            result = result + self.stream.read(self.CHUNK)

        return np.fromstring(result, 'Float32')

    def read_old(self, number_of_blocks):
        result = ()

        for i in range(number_of_blocks):
            data = self.stream.read(self.CHUNK)
            result = result + struct.unpack(str(2 * self.CHUNK) + 'B', data)

        return np.array(result, dtype='b')[::2]

    def exit_app(self):
        print('stream closed')
        self.pyaudio.close(self.stream)
