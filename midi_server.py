import mido
import sys
import harmony
from pythonosc.udp_client import SimpleUDPClient
import json
import time
import random

midi_in_buffer_size = 8  # notes to receive before a mode switch
ip = "127.0.0.1"
port = 1337
notes_per_second = 0
osc_trigger = 0

if __name__ == '__main__':
    # command line feedback for users
    midi_input_names = mido.get_input_names()

    if len(sys.argv) <= 1:
        print('usage: python midi_server.py midi_port\n',
              'midi ports: {}'.format(midi_input_names),
              sep='\n')
        exit(-1)

    midi_in = int(sys.argv[1])

    print('selected midi input: {}'.format(midi_input_names[midi_in]),
          '',
          sep='\n')
    # --------------------------------------------

    # setting up OSC
    osc_client = SimpleUDPClient(ip, port)  # Create client


    # initializing harmonic state
    harmonicState = harmony.HarmonicState()

    # setting up midi in
    midi_in_buffer = []

    # receiving midi messages
    with mido.open_input(midi_input_names[midi_in]) as midi_in_port:
        timer_start = time.time()  # starting a timer
        for midi_msg in midi_in_port:
            if midi_msg.type == 'note_on':
                midi_in_buffer.append(midi_msg)
                print(midi_msg)
            if len(midi_in_buffer) > midi_in_buffer_size:
                harmonicState.push_notes(midi_in_buffer)
                current_mode = harmonicState.change_mode()
                midi_in_buffer = []
                notes_per_second = midi_in_buffer_size / (time.time() - timer_start)
                timer_start = time.time()  # resetting the timer

                # sending an OSC message to the sequencer and the visuals
                # script containing the mode
                osc_client.send_message('/sequencer/settings', [json.dumps(current_mode), notes_per_second])
                osc_client.send_message('/visuals/mode', random.randint(3, 7))  # TODO: send a proper message

                # logging mode status
                print('current mode',
                      'root: {}'.format(harmonicState.currentMode['root']),
                      'mode_signature_index: {}'.format(harmonicState.currentMode['mode_signature_index']),
                      'mode_index: {}'.format(harmonicState.currentMode['mode_index']),
                      'notes_per_second: {}'.format(notes_per_second),
                      '',
                      sep='\n')
