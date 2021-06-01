import melodically
import threading
import mido
import time


class Sequencer:
    def __init__(self, sequence_port, chord_port, rhythm_port, bpm=74):
        # TODO: comments
        self.sequenceOutPort = sequence_port
        self.chordOutPort = chord_port
        self.rhythmOutPort = rhythm_port
        self.bpm = bpm
        self.midiChannel = 0
        self.durations = melodically.get_durations(self.bpm)
        self.thread1 = threading.Thread(target=self.run_sequences)
        self.thread2 = threading.Thread(target=self.run_chords)
        self.thread3 = threading.Thread(target=self.run_rhythm)
        self.playSequenceEvent = threading.Event()
        self.playChordEvent = threading.Event()
        self.playRhythmEvent = threading.Event()
        self.lock = threading.Lock()
        self.sequence = []
        self.chord_notes = []
        self.rhythmNote = 24

        self.thread1.start()
        self.thread2.start()
        self.thread3.start()

    def set_bpm(self, bpm):
        self.durations = melodically.get_durations(bpm)
        self.bpm = bpm

    def play(self, sequence, chord_notes, rhythm_note, midi_channel):
        # critical section
        with self.lock:
            self.sequence = sequence
            self.chord_notes = chord_notes
            self.midiChannel = midi_channel
            self.rhythmNote = rhythm_note
        # end of critical section

        self.playChordEvent.set()
        self.playRhythmEvent.set()
        if sequence:
            self.playSequenceEvent.set()

    def run_rhythm(self):
        rhythm_sequence = ['4', '4', '4', '4']
        rhythm_sequence = melodically.clip_rhythmic_sequence(rhythm_sequence, 1)

        while True:
            self.playRhythmEvent.wait()
            self.playRhythmEvent.clear()

            with self.lock:  # critical section
                rhythm_note = self.rhythmNote
                channel = self.midiChannel - 1
                durations = self.durations.copy()
            # end of critical section

            note_on = mido.Message('note_on', note=rhythm_note, channel=channel)
            note_off = mido.Message('note_off', note=rhythm_note, channel=channel)

            with mido.open_output(self.rhythmOutPort) as outport:
                for step in rhythm_sequence:
                    outport.send(note_on)
                    time.sleep(durations[step])
                    outport.send(note_off)

    def run_sequences(self):
        while True:
            self.playSequenceEvent.wait()
            self.playSequenceEvent.clear()

            with self.lock:  # critical section
                sequence = self.sequence.copy()
                channel = self.midiChannel - 1
            # end of critical section

            with mido.open_output(self.sequenceOutPort) as outport:
                for step in sequence:
                    with self.lock:  # critical section
                        duration = self.durations[step['duration'].replace('r', '')]
                    # end of critical section

                    note_on = mido.Message('note_on', note=step['note'], channel=channel)
                    note_off = mido.Message('note_off', note=step['note'], channel=channel)

                    if 'r' not in step['duration']:
                        outport.send(note_on)

                    time.sleep(duration)

                    if 'r' not in step['duration']:
                        outport.send(note_off)

    def run_chords(self):
        with self.lock:  # critical section
            one_measure_seconds = self.durations['1']
        # end of critical section

        while True:
            self.playChordEvent.wait()
            self.playChordEvent.clear()

            with mido.open_output(self.chordOutPort) as outport:

                with self.lock:  # critical section
                    chord_notes = self.chord_notes.copy()
                    channel = self.midiChannel - 1
                # end of critical section

                messages_note_on = [mido.Message('note_on', note=x, channel=channel) for x in chord_notes]
                messages_note_off = [mido.Message('note_off', note=x, channel=channel) for x in chord_notes]

                for note_on in messages_note_on:
                    outport.send(note_on)

                time.sleep(one_measure_seconds)

                for note_off in messages_note_off:
                    outport.send(note_off)
