import numpy as np
import mido
from collections import Counter

"""
list of notes in standard notation
"""
note_std_list = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']

"""
this data structure contains all the
possible semitone sequences to construct
the modes;

each row defines a mode family
"""
semitone_sequences = [
    [2, 2, 1, 2, 2, 2, 1],  # TTSTTTS
    [2, 2, 1, 3, 1, 2, 1],
]


def midi_to_std(midi_note):
    """
    converts a midi note to standard note notation

    :param midi_note: midi note number
    :return: note in standard notation
    """
    return note_std_list[midi_note % 12]


def get_root(notes_std):
    """
    infers a root note from a list,
    choosing the most played

    :param notes_std: notes in standard notation
    :return: single note in standard notation
    """
    return Counter(notes_std).most_common(1)[0][0]


def get_all_modes(root):
    """
    given a root note, generates all the possible modes

    :param root: note in standard notation
    :return: multi dimensional list of size [mode_families x 7 x 7] containing notes in standard notation
    """
    modes_note_std = []
    for i in range(len(semitone_sequences)):  # iterating for different modes families
        modes_note_std.append([])
        current_sequence = np.array(semitone_sequences[i])
        for j in range(7):  # iterating for each mode in the family
            modes_note_std[i].append([root])
            last_note = note_std_list.index(root)
            for k in range(6):  # iterating for each note in the scale
                last_note = (last_note + current_sequence[k]) % 12
                modes_note_std[i][j].append(note_std_list[last_note])
            current_sequence = np.roll(current_sequence, -1)  # circular shift of the note sequence
    return modes_note_std


def get_all_modes_for_each_note():
    return {note: get_all_modes(note) for note in note_std_list}


def harmonic_distances(modes, notes_std):
    # TODO: implementation
    # step2: check the how many note are in the scale and how many not, and assign a distance to each
    pass


all_modes = get_all_modes_for_each_note()


class Improvisor:
    def __init__(self):
        self.midiNoteList = []  # contains midi note, time information and probability
        self.currentMode = {'root': 'C', 'mode_family_index': 0, 'mode_index': 0}

    def push_notes(self, note_messages):
        """
        pushes new notes messages inside midiNoteList

        :param note_messages: contains the midi note, the absolute ticks for start and end
        """
        notes_and_probability = [{'midi': msg, 'probability': 0} for msg in note_messages]
        self.midiNoteList.append(notes_and_probability)

    def next_mode(self):
        notes_std = [midi_to_std(note['midi']) for note in self.midiNoteList]
        root = get_root(notes_std)
        modes_distance = harmonic_distances(all_modes[root])
        mode_family_index = modes_distance.index(min(modes_distance))
        nearest_mode_family = modes_distance[mode_family_index]
        mode_index = nearest_mode_family.index(min(nearest_mode_family))

        self.currentMode['root'] = root
        self.currentMode['mode_family_index'] = mode_family_index
        self.currentMode['mode_index'] = mode_index


def read_midi(midi_path):
    print("reading midi file " + midi_path)
    midi_file = mido.MidiFile(midi_path)
    midi_track = midi_file.tracks[0]  # discarding all other tracks
    note_on_list = [msg for msg in midi_track if msg.type == 'note_on']
    note_off_list = [msg for msg in midi_track if msg.type == 'note_off']

    notes = []
    current_tick_padding = 0
    for i in range(len(note_on_list)):
        current_note_on = note_on_list[i]
        current_note_off = note_off_list[i]
        abs_start = current_tick_padding + current_note_on.time
        current_tick_padding = abs_start + current_note_off.time
        new_note = {
            'midi_note': current_note_on.note,
            'abs_start': abs_start,
            'abs_end': current_tick_padding
        }
        notes.append(new_note)

    for note in notes:
        print(note)
