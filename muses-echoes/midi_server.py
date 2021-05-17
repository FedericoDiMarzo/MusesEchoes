import mido
import sys
import melodically
import markov_chains
from pythonosc.udp_client import SimpleUDPClient
import json
import time
import random

midi_in_buffer_size = 8  # notes to receive before a mode switch
ip = "127.0.0.1"
port = 1337
notes_per_second = 0
osc_trigger = 0


class MidiServer:
    def __init__(self, midi_port, ip="127.0.0.1", osc_port=1337, buffer_size=64):
        self.midiPort = midi_port
        self.ip = ip
        self.oscPort = osc_port
        self.bufferSize = buffer_size

        # setting up OSC
        self.oscClient = SimpleUDPClient(ip, osc_port)

        self.harmonicState = melodically.HarmonicState(buffer_size)

        self.melodyMarkovChain = markov_chains.AbstractMelodyMarkovChain(order=3)

        self.durations = melodically.get_durations(74)  # TODO: bpm

        self.midiNoteQueue = melodically.MidiNoteQueue()

        # setting up midi in
        self.midiBuffer = []

    def listen_midi(self):
        # receiving midi messages
        with mido.open_input(self.midiPort) as midi_in_port:
            for midi_msg in midi_in_port:
                if midi_msg.type == 'note_on' or 'note_off':
                    self.midiBuffer.append(midi_msg)
                    self.midiNoteQueue.push(midi_msg.type, midi_msg.note)
                    print(midi_msg)
                if len(self.midiBuffer) >= self.bufferSize:
                    # updating the harmonic state
                    new_notes = [melodically.midi_to_std(msg.note) for msg in self.midiBuffer if msg.type == 'note_on']
                    self.harmonicState.push_notes(new_notes)
                    current_mode = self.harmonicState.get_mode_notes()
                    self.midiBuffer = []

                    # parsing the input melody
                    # TODO: Andre debugging
                    current_chord = 'CM'  # TODO: use the markov chain to change chords
                    parsed_melody = melodically.parse_melody(self.midiNoteQueue, current_chord, self.durations)
                    self.midiNoteQueue.clear()

                    # markov chain for the melody
                    self.melodyMarkovChain.learn_melody(parsed_melody)
                    generated_melody = self.melodyMarkovChain.generate_new_melody(8)  # TODO: sync with the sequencer

                    # sending an OSC message to the sequencer and the visuals
                    # script containing the mode
                    # osc_client.send_message('/sequencer/settings', [json.dumps(current_mode), notes_per_second])
                    # osc_client.send_message('/visuals/mode', random.randint(3, 7))  # TODO: send a proper message

                    # logging
                    print('current scale: {}'.format(current_mode))
                    print('parsed melody: {}'.format(parsed_melody))
                    print('generated melody: {}'.format(generated_melody))


if __name__ == '__main__':
    # command line feedback for users
    midi_input_names = mido.get_input_names()

    if len(sys.argv) <= 1:
        print('usage: python -m midi_server.py midi_port\n',
              'midi ports: {}'.format(midi_input_names),
              sep='\n')
        exit(-1)

    midi_index = int(sys.argv[1])

    print('selected midi input: {}'.format(midi_input_names[midi_index]),
          '',
          sep='\n')
    # --------------------------------------------

    midiServer = MidiServer(midi_input_names[midi_index], buffer_size=16)
    midiServer.listen_midi()
