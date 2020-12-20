import lib.braid as braid
import numpy as np
from harmony import mode_signatures, std_to_midi
import mido
import sys
from pythonosc.osc_server import BlockingOSCUDPServer, Dispatcher
from threading import Thread, Lock
import json

test_tracks = {
    1: (1, 0),
    2: (3, 5, 3, 7),
    3: (5, 3),
}

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
        self.tracks = {}
        # braid.log_midi(True)

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
        braid.play()


def setup_tracks(seq):
    for key, value in test_tracks.items():
        seq.add_track(key)
        seq.set_pattern(key, value)


def osc_server_setup():
    print('OSC server running')
    dispatcher = Dispatcher()
    dispatcher.map("/sequencer/*", osc_handler)
    server = BlockingOSCUDPServer((ip, port), dispatcher)
    server.serve_forever()  # Blocks forever


def osc_handler(address, *args):
    # TODO: check for possible concurrency issues
    mode = json.loads(args[0])
    print('OSC address: {}'.format(address))
    print('current mode',
          'root: {}'.format(mode['root']),
          'mode_signature_index: {}'.format(mode['mode_signature_index']),
          'mode_index: {}'.format(mode['mode_index']),
          '',
          sep='\n')
    sequencer.change_mode(mode)




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
    sequencer.set_bpm(50)
    sequencer.change_mode({'root': 'C', 'mode_signature_index': 0, 'mode_index': 0})
    sequencer.play()
