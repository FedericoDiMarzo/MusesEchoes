import threading
import time


class Sequencer:
    def __init__(self, bpm=60):
        self.bpm = bpm
        self.phraseLen = 8  # in beats
        self.thread = threading.Timer(self.get_phrase_seconds(), self.next_phrase_callback)
        self.changingMode = False

    def next_phrase_callback(self):
        if self.changingMode:
            # TODO: updating thread
            self.thread.cancel()
            self.changingMode = False

        # TODO: updating the model
        return

    def set_bpm(self, bpm):
        self.bpm = bpm
        self.changingMode = True

    def get_phrase_seconds(self):
        return self.phraseLen * 60 / self.bpm
