import threading
import time


class Sequencer:
    """
    Class used to spawn a periodic thread based on bpm,
    used to handle the model update and send midi/osc messages
    """

    def __init__(self, bpm=60):
        """
        :param bpm: beats per minute
        """
        self.bpm = bpm
        self.phraseLen = 4  # in beats
        self.thread = threading.Timer(self.get_phrase_seconds(), self.next_phrase_callback)
        self.done = False

    def start(self):
        """
        starts the sequencer thread
        """
        print('sequencer started')
        self.thread.start()

    def next_phrase_callback(self):
        """
        thread function for the sequencer
        """
        while not self.done:
            # TODO: updating the model
            print('next_phrase_callback() called')
            time.sleep(self.get_phrase_seconds())

    def set_bpm(self, bpm):
        """
        sets the bpm

        :param bpm: beats per minute
        """
        print('bpm changed')
        self.bpm = bpm

    def get_phrase_seconds(self):
        """
        bpm seconds conversion based on phraseLen

        :return: phrase length in seconds
        """
        return self.phraseLen * 60 / self.bpm

    def close(self):
        print('sequencer closed')
        self.done = True

