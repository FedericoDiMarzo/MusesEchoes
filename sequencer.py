import lib.braid as braid
import numpy as np


def get_scale_from_mode(mode_signature, mode_index):
    rolled_mode_signature = list(np.roll(mode_signature, -mode_index))
    braid_semitones = [0]
    for index in range(6):
        braid_semitones.append(braid_semitones[index] + rolled_mode_signature[index])

    return braid_semitones


class Sequencer:
    def __init__(self, midi_out):
        braid.midi_out = midi_out

    def set_bpm(self, bpm):
        print('bpm changed: {}'.format(bpm))
        braid.tempo(bpm)
