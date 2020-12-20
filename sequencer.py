import lib.braid as braid
import numpy as np
from harmony import mode_signatures, std_to_midi

test_tracks = {
    1: (1, 0),
    2: (3, 5, 3, 7),
    3: (5, 3),
}


def get_scale_from_mode(mode_signature, mode_index):
    rolled_mode_signature = list(np.roll(mode_signature, -mode_index))
    braid_semitones = [0]
    for index in range(6):
        braid_semitones.append(braid_semitones[index] + rolled_mode_signature[index])

    return braid.Scale(braid_semitones)


class Sequencer:
    def __init__(self, midi_out):
        braid.midi_out = midi_out
        self.tracks = {}
        braid.log_midi(True) # TODO: debug

    def set_bpm(self, bpm):
        print('bpm changed: {}'.format(bpm))
        braid.tempo(bpm)

    def change_mode(self, mode):
        mode_sig = mode_signatures[mode['mode_signature_index']]
        scale = get_scale_from_mode(mode_sig, mode['mode_index'])
        for t in self.tracks.values():
            t.chord = std_to_midi(mode['root']), scale

    def add_track(self, midi_channel):
        self.tracks[midi_channel] = braid.Thread(midi_channel)

    def set_pattern(self, track_number, pattern):
        self.tracks[track_number].pattern = pattern

    def play(self):
        for t in self.tracks.values():
            t.start()
        braid.play()
