import lib.braid as braid
import numpy as np
from harmony import mode_signatures, std_to_midi
import mido
import sys
from pythonosc.osc_server import BlockingOSCUDPServer, Dispatcher
from threading import Thread
import json

ip = "127.0.0.1"
port = 1337
sequencer = None


def get_scale_from_mode(mode_signature, mode_index):
    rolled_mode_signature = list(np.roll(mode_signature, -mode_index))
    braid_semitones = [0]
    for index in range(6):
        braid_semitones.append(braid_semitones[index] + rolled_mode_signature[index])

    return braid.Scale(braid_semitones)


class Sequencer:
    def __init__(self, midi_out):
        braid.midi_out = midi_out
        self.complexity = 0  # 0 simple, 1 complex
        self.tracks = {}
        self.scores = {}
        # braid.log_midi(True)

    def set_bpm(self, bpm):
        print('bpm changed: {}'.format(bpm))
        braid.tempo(bpm)

    def calculate_complexity(self, notes_per_seconds):
        max_notes_per_seconds = 10  # TODO: fine tune the value
        self.complexity = min(max_notes_per_seconds, notes_per_seconds) / max_notes_per_seconds
        print('sequencer complexity: {}'.format(self.complexity))

    def change_mode(self, mode):
        mode_sig = mode_signatures[mode['mode_signature_index']]
        scale = get_scale_from_mode(mode_sig, mode['mode_index'])
        for t in self.tracks.values():
            t.chord = std_to_midi(mode['root']), scale

    def add_track(self, midi_channel):
        self.tracks[midi_channel] = braid.Thread(midi_channel)

    def set_score(self, track_number, score):
        self.scores[track_number] = score

    def set_pattern(self, track_number):
        simple_pattern = self.scores[track_number]['simple']
        complex_pattern = self.scores[track_number]['complex']
        blended_pattern = braid.blend(simple_pattern, complex_pattern, self.complexity)
        print(blended_pattern)  # TODO: remove print
        self.tracks[track_number].pattern = blended_pattern

    def play(self):
        braid.play()


def setup_tracks(seq):
    seq.add_track(1)
    seq.add_track(2)
    seq.add_track(3)

    score1 = {
        'simple': (1, 0, 0, braid.Z),
        'complex': (1, 0, 0, braid.Z)
    }

    score2 = {
        'simple': ([3, 5], 0, [5, 3], 0),
        'complex': ([5, 7], [5, [5, 3]], [5, 1], [1, [5, 1]])
    }

    score3 = {
        'simple': (0, 5, 1, 0),
        'complex': ([3, [5, 3]], [[3, 7], 3], [[5, 5, 5], 3], [5, [7, 5, 3, 5], [7, 5]])
    }

    seq.set_score(1, score1)
    seq.set_score(2, score2)
    seq.set_score(3, score3)
    seq.set_pattern(1)
    seq.set_pattern(2)
    seq.set_pattern(3)


def osc_server_setup():
    print('OSC server running')
    dispatcher = Dispatcher()
    dispatcher.map("/sequencer/*", osc_handler)
    server = BlockingOSCUDPServer((ip, port), dispatcher)
    server.serve_forever()  # Blocks forever


def osc_handler(address, *args):
    # TODO: check for possible concurrency issues
    mode = json.loads(args[0])
    notes_per_second = float(args[1])
    print('OSC address: {}'.format(address))
    print('current mode',
          'root: {}'.format(mode['root']),
          'mode_signature_index: {}'.format(mode['mode_signature_index']),
          'mode_index: {}'.format(mode['mode_index']),
          'notes_per_second: {}'.format(notes_per_second),
          '',
          sep='\n')
    sequencer.change_mode(mode)
    sequencer.calculate_complexity(notes_per_second)
    for i in range(len(sequencer.tracks)):
        sequencer.set_pattern(i+1)


if __name__ == '__main__':
    midi_output_names = mido.get_output_names()

    if len(sys.argv) <= 1:
        print('usage: python sequencer.py midi_port\n',
              'midi ports: {}'.format(midi_output_names),
              sep='\n')
        exit(-1)

    # OSC
    osc_thread = Thread(target=osc_server_setup)
    osc_thread.start()

    # setting up midi out
    midi_out = int(sys.argv[1])

    # setting up the sequencer
    sequencer = Sequencer(midi_out)
    setup_tracks(sequencer)
    sequencer.set_bpm(80)
    sequencer.change_mode({'root': 'C', 'mode_signature_index': 0, 'mode_index': 0})
    sequencer.play()
