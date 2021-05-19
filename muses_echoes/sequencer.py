import melodically
import threading
import mido
import time


class Sequencer:
    def __init__(self, midi_out_port, bpm=74):
        self.midiOutPort = midi_out_port
        self.bpm = bpm
        self.durations = melodically.get_durations(self.bpm)
        self.thread = threading.Thread(target=self.run)
        self.playEvent = threading.Event()
        self.lock = threading.Lock()
        self.sequence = []
        self.thread.start()

    def set_bpm(self, bpm):
        self.durations = melodically.get_durations(bpm)
        self.bpm = bpm

    def play_sequence(self, sequence):
        # critical section
        with self.lock:
            self.sequence = sequence
        # end of critical section

        if sequence:
            self.playEvent.set()

    def run(self):
        while True:
            # TODO: bug the sequence loops even with the event lock
            self.playEvent.wait()
            self.playEvent.clear()

            with mido.open_output(self.midiOutPort) as outport:
                # critical section
                with self.lock:
                    for step in self.sequence:
                        note_on = mido.Message('note_on', note=step['note'])
                        note_off = mido.Message('note_off', note=step['note'])

                        if 'r' not in step['duration']:
                            outport.send(note_on)

                        time.sleep(self.durations[step['duration'].replace('r', '')])

                        if 'r' not in step['duration']:
                            outport.send(note_off)
                # end of critical section
