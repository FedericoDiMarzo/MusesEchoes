import mido
import sys
import harmony

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
          sep='\n')
    # --------------------------------------------

    harmonicState = harmony.HarmonicState()

