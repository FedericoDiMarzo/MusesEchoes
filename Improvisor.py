"""
dictionary used to connect note names to numbers
"""
notenum_dict = {'C': 0, 'C#': 1, 'D': 2, 'D#': 3, 'E': 4, 'F': 5,
                'F#': 6, 'G': 7, 'G#': 8, 'A': 9, 'A#': 10, 'B': 11}

"""
this data structure contains all the
possible semitone sequences to construct
the modes
"""
semitone_sequences = [
    [2, 2, 1, 2, 2, 2, 1],  # TTSTTTS
    [2, 2, 1, 2, 3, 2, 1],
]


def midi_to_notenum(midinote):
    notenum = midinote%12
    return notenum


def get_root(notes):
    # TODO: extract root from most frequent note
    pass


def harmonic_distance(root, semitone_sequence, notes):
    # TODO: implementation
    # step1: extract all the possible modes from the root
    # step2: check the how many note are in the scale and how many not, and assign a distance to each
    pass


class Improvisor:
    def __init__(self):
        self.noteQueue = []
        self.currentMode = {'root': 'C', 'semitone_sequence_index': 0, 'mode_index': 0}

    def push_notes(self, new_notes):
        notes_and_probability = [{'midi': note, 'probability': 0} for note in new_notes]
        self.noteQueue.append(notes_and_probability)

    def next_mode(self):
        notes = [note['midi'] for note in self.noteQueue]
        root = get_root(notes)
        modes_distance = harmonic_distance(root, notes)
        semitone_sequences_index = modes_distance.index(min(modes_distance))
        tmp = modes_distance[semitone_sequences_index]  # sequence with the lowest distance
        mode_index = tmp.index(min(tmp))

        self.currentMode['root'] = root
        self.currentMode['semitone_sequence_index'] = semitone_sequences_index
        self.currentMode['mode_index'] = mode_index
