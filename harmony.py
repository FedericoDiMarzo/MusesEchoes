import numpy as np
from collections import Counter

"""
list of notes in standard notation
"""
note_std_list = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']

"""
this data structure contains all the
possible semitone sequences to construct
many families of modes
"""
mode_signatures = [
    [2, 2, 1, 2, 2, 2, 1],  # TTSTTTS
    [2, 2, 1, 3, 1, 2, 1],
]


def midi_to_std(midinote):
    """
    converts a midi note to standard note notation

    :param midinote: midi note number
    :return: note in standard notation
    """
    return note_std_list[midinote % 12]


def get_root(notes):
    """
    returns the most common value in the list of notes

    :param notes: notes in standard notation
    :return: single note in standard notation
    """
    return max(set(notes), key=notes.count)


def get_all_modes(root):
    """
    given a root, calculates all the modes

    :param root: note in std notation
    :return: multi dimensional list of size [len(mode_signatures)x7x7] containing the modes
    """
    modes_note_std = []
    for i in range(len(mode_signatures)):  # iterating for different modes families
        modes_note_std.append([])
        current_sequence = np.array(mode_signatures[i])
        for j in range(7):  # iterating for each mode in the family
            modes_note_std[i].append([root])
            last_note = note_std_list.index(root)
            for k in range(6):  # iterating for each note in the scale
                last_note = (last_note + current_sequence[k]) % 12
                modes_note_std[i][j].append(note_std_list[last_note])
            current_sequence = np.roll(current_sequence, -1)  # circular shift of the note sequence
    return modes_note_std


"""
dictionary containing all the notes as keys and
the respective modes as value
"""
modes_dict = {root: get_all_modes(root) for root in note_std_list}


def harmonic_affinities(modes, notes_std):
    # returns a multi dim list of size [len(mode_signatures)x7]
    positive_weights = [0.3, 0.06, 0.08, 0.08, 0.24, 0.16, 0.08]
    negative_weight = 0.2
    input_notes_len = len(notes_std)
    counter = Counter(notes_std)
    affinities = []
    for i in range(len(mode_signatures)):
        affinities.append([])
        for j in range(7):
            curr_mode = modes[i][j]  # list of 7 notes
            aff = 0
            for k in range(7):
                # calculating the positive weights
                aff = aff + counter[curr_mode[k]] * positive_weights[k]
            not_in_the_mode = [note for note in notes_std if note not in curr_mode]
            aff = aff - len(not_in_the_mode) * negative_weight
            aff = aff / input_notes_len
            affinities[i].append(aff)

    return affinities


class HarmonicState:
    def __init__(self):
        self.midiNoteBuffer = []
        self.bufferSize = 128  # TODO: test this value
        self.currentMode = {'root': 'C', 'mode_signature_index': 0, 'mode_index': 0}

    def push_notes(self, midi_notes):
        self.midiNoteBuffer.append(midi_notes)

    def next_mode(self):
        notes_std = [midi_to_std(midi_msg.note) for midi_msg in self.midiNoteBuffer]  # TODO: test it
        root = get_root(notes_std)
        modes_affinities = harmonic_affinities(root, notes_std)
        mode_signature_index = modes_affinities.index(max(modes_affinities))
        tmp = modes_affinities[mode_signature_index]  # sequence with the lowest distance
        mode_index = tmp.index(max(tmp))

        self.currentMode['root'] = root
        self.currentMode['mode_signature_index'] = mode_signature_index
        self.currentMode['mode_index'] = mode_index
