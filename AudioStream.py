import numpy as np
import pyaudio
import matplotlib.pyplot as plt
import struct
import sys
import time


class AudioStream(object):
    """
    Stream of audio, implemented with pyaudio
    """

    def __init__(self, rate):
        """
        :param rate: sample frequency
        """
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
        print('stream opened')

    def read(self, number_of_blocks):
        """
        reads from the stream

        :param number_of_blocks: number of blocks of size chunk to read
        :return: numpy float array containing the audio
        """
        result = b''  # empty binary string

        for i in range(number_of_blocks):
            result = result + self.stream.read(self.CHUNK)

        return np.fromstring(result, 'Float32')

    def close(self):
        """
        closes the stream
        """
        self.pyaudio.close(self.stream)
        print('stream closed')
