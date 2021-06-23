import sys
import mido
from muses_echoes.muses import MuseEchoes

"""
Change these variables to easily modify the
settings of the application.
"""
_osc_ip = "127.0.0.1"
_osc_port = 1337
_midi_buffer_size = 8
_midi_mapping = [2, 1, 1, 2, 2, 1, 1]  # 1: I-V / 2: II-VI / 3: III-IV-VII
# _midi_mapping = [1, 1, 1, 1, 1, 1, 1]  # TODO: Test
_bpm = 74
_measures_for_scale_change = 4
_melody_octave_range = (4, 5)
_chord_octave_range = (3, 4)
_rhythm_midi_note = 36  # C2
_markov_chains_order = 3
_markov_chains_inertia = 0.78

if __name__ == '__main__':
    # =========================================
    # command line feedback for the users
    # =========================================
    midi_input_names = mido.get_input_names()
    midi_output_names = mido.get_output_names()

    if len(sys.argv) <= 3:
        print('usage: python -m muses_echoes [in] [melodies] [chords] [rhythm]',
              '__________\n',
              'midi in ports: {}'.format(midi_input_names),
              'midi out ports: {}'.format(midi_output_names),
              '__________\n',
              '[in]: midi in port index used to receive notes',
              '[melodies]: midi out port index used to send notes for the melody',
              '[chords]: midi out port index used to send notes for the chords',
              '[rhythm]: midi out port index used to send notes for the rhythm',
              '',
              sep='\n')
        exit(-1)

    midi_in_index = int(sys.argv[1])
    midi_sequence_out_index = int(sys.argv[2])
    midi_chord_out_index = int(sys.argv[3])
    midi_rhythm_out_index = int(sys.argv[4])
    print('selected midi input: {}'.format(midi_input_names[midi_in_index]),
          'selected midi sequence output: {}'.format(midi_output_names[midi_sequence_out_index]),
          'selected midi chord output: {}'.format(midi_output_names[midi_chord_out_index]),
          'selected midi rhythm output: {}'.format(midi_output_names[midi_rhythm_out_index]),
          '',
          sep='\n')
    # =========================================
    # =========================================

    # creating and starting the multi-threaded application
    midiServer = MuseEchoes(
        midi_in_port=midi_input_names[midi_in_index],
        midi_sequence_out_port=midi_output_names[midi_sequence_out_index],
        midi_chord_out_port=midi_output_names[midi_chord_out_index],
        midi_rhythm_out_port=midi_output_names[midi_rhythm_out_index],
        midi_mapping=_midi_mapping,
        osc_ip=_osc_ip,
        osc_port=_osc_port,
        midi_buffer_size=_midi_buffer_size,
        bpm=_bpm,
        measures_for_scale_change=_measures_for_scale_change,
        melody_octave_range=_melody_octave_range,
        chord_octave_range=_chord_octave_range,
        rhythm_midi_note=_rhythm_midi_note,
        markov_chains_order=_markov_chains_order,
        markov_chains_inertia=_markov_chains_inertia
    )
    midiServer.start()
