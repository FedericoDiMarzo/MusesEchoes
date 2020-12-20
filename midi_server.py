import mido
import sys
import harmony
from sequencer import Sequencer, test_tracks

midi_in_buffer_size = 8  # notes to receive before a mode switch


def setup_tracks(sequencer):
    for key, value in test_tracks.items():
        sequencer.add_track(key)
        sequencer.set_pattern(key, value)


if __name__ == '__main__':
    # command line feedback for users
    midi_input_names = mido.get_input_names()
    midi_output_names = mido.get_output_names()

    if len(sys.argv) <= 2:
        print('usage: python midi_server.py midiIn midiOut\n',
              'midi in ports: {}'.format(midi_input_names),
              'midi out ports: {}'.format(midi_output_names),
              sep='\n')
        exit(1)

    midi_in = int(sys.argv[1])
    midi_out = int(sys.argv[2])

    print('selected midi input: {}'.format(midi_input_names[midi_in]),
          'selected midi output: {}'.format(midi_output_names[midi_out]),
          '',
          sep='\n')
    # --------------------------------------------

    # initializing harmonic state
    harmonicState = harmony.HarmonicState()

    # setting up midi out
    sequencer = Sequencer(midi_out)
    setup_tracks(sequencer)
    sequencer.set_bpm(50)
    sequencer.change_mode(harmonicState.currentMode)
    sequencer.play()

    # setting up midi in
    midi_in_buffer = []

    with mido.open_input(midi_input_names[midi_in]) as midi_in_port:
        for midi_msg in midi_in_port:
            if midi_msg.type == 'note_on':
                midi_in_buffer.append(midi_msg)
                print(midi_msg)
            if len(midi_in_buffer) > midi_in_buffer_size:
                harmonicState.push_notes(midi_in_buffer)
                current_mode = harmonicState.change_mode()
                midi_in_buffer = []
                sequencer.change_mode(current_mode)

                # logging mode status
                print('current mode',
                      'root: {}'.format(harmonicState.currentMode['root']),
                      'mode_signature_index: {}'.format(harmonicState.currentMode['mode_signature_index']),
                      'mode_index: {}'.format(harmonicState.currentMode['mode_index']),
                      '\n',
                      sep='\n')
