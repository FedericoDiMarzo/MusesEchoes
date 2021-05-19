# TODO: change mode if N x notes are detected
import sys
import mido
from muses_echoes.application import MuseEchoes

"""
Change these variables to easily modify the
settings of the application.
"""
_osc_ip = "127.0.0.1"
_osc_port = 1337
_midi_buffer_size = 10
_bpm = 74
_measures_for_scale_change = 4
_melody_octave_range = (4, 6)

if __name__ == '__main__':
    # =========================================
    # command line feedback for the users
    # =========================================
    midi_input_names = mido.get_input_names()
    midi_output_names = mido.get_output_names()

    if len(sys.argv) <= 3:
        print('usage: python -m muses_echoes midi_in_port_index midi_out_port_index\n',
              'midi in ports: {}'.format(midi_input_names),
              'midi out ports: {}'.format(midi_output_names),
              sep='\n')
        exit(-1)

    midi_in_index = int(sys.argv[1])
    midi_sequence_out_index = int(sys.argv[2])
    midi_chord_out_index = int(sys.argv[3])
    print('selected midi input: {}'.format(midi_input_names[midi_in_index]),
          'selected midi sequence output: {}'.format(midi_output_names[midi_sequence_out_index]),
          'selected midi chord output: {}'.format(midi_output_names[midi_chord_out_index]),
          '',
          sep='\n')
    # =========================================
    # =========================================

    # creating and starting the multi-threaded application
    midiServer = MuseEchoes(
        midi_in_port=midi_input_names[midi_in_index],
        midi_sequence_out_port=midi_output_names[midi_sequence_out_index],
        midi_chord_out_port=midi_output_names[midi_chord_out_index],
        osc_ip=_osc_ip,
        osc_port=_osc_port,
        midi_buffer_size=_midi_buffer_size,
        bpm=_bpm,
        measures_for_scale_change=_measures_for_scale_change,
        melody_octave_range=_melody_octave_range,
    )
    midiServer.start()
