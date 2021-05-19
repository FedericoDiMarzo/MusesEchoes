import mido
import melodically
import muses_echoes.markov_chain as markov_chain
import threading
from pythonosc.udp_client import SimpleUDPClient
import json
import time
import random
from muses_echoes.sequencer import Sequencer

# degree to number mapping
degrees = ['I', 'II', 'III', 'IV', 'V', 'VI', 'VII']


class MuseEchoes:
    def __init__(self, midi_in_port,
                 midi_sequence_out_port, midi_chord_out_port,
                 midi_buffer_size=10,
                 osc_ip="127.0.0.1", osc_port=1337,
                 bpm=74, measures_for_scale_change=4,
                 melody_octave_range=(4, 6),
                 chord_octave_range=(2, 5)):

        # lock used to protect the critical sections
        self.lock = threading.Lock()

        # event triggered when a scale must be changed
        self.changeScaleEvent = threading.Event()

        # event triggered when a scale change is completed
        self.changeScaleDoneEvent = threading.Event()

        # event triggered when the sequencer should execute a new melody
        self.sequencerEvent = threading.Event()

        # event triggered when the midi buffer is full
        self.bufferFullEvent = threading.Event()

        # name of the midi ports
        self.midiInPort = midi_in_port
        self.midiSequenceOutPort = midi_sequence_out_port
        self.midiChordOutPort = midi_chord_out_port

        # ip for the osc protocol
        self.oscIp = osc_ip

        # port for the osc protocol
        self.oscPort = osc_port

        # length of the midi buffer used for the input
        self.midiBufferLen = midi_buffer_size

        # used to buffer the notes in std notation used for the harmonicState
        self.noteBuffer = []

        # counter for the measures
        self.measureCount = 0

        # setting up OSC
        self.oscClient = SimpleUDPClient(osc_ip, osc_port)

        # midi note queue shared between the threads
        self.midiNoteQueue = melodically.MidiNoteQueue()

        # used to change the scale
        self.harmonicState = melodically.HarmonicState(buffer_size=self.midiBufferLen * 3)  # TODO: fine tune this value

        # current modal scale
        self.currentScale = []

        # current chord sequence
        self.chordSequence = []

        # tempo in beats per minutes
        self.bpm = bpm

        # dictionary containing the durations for each rhythmic figure
        self.durations = melodically.get_durations(self.bpm)

        # removing triplets from the durations dictionary
        del self.durations['16t']
        del self.durations['8t']
        del self.durations['4t']

        # number of measures for triggering a scale change
        self.measuresForScaleChange = measures_for_scale_change

        # range of octaves for the generated melody and for the chords
        self.melodyOctaveRange = melody_octave_range
        self.chordOctaveRange = chord_octave_range

        # midi sequencer
        self.sequencer = Sequencer(sequence_port=self.midiSequenceOutPort,
                                   chord_port=self.midiChordOutPort,
                                   bpm=self.bpm)

    def start(self):
        """
        Starts all the threads of the application and joins them.
        """
        thread1 = threading.Thread(target=self.listen_midi)
        thread2 = threading.Thread(target=self.fire_events)
        thread3 = threading.Thread(target=self.play_midi)
        thread4 = threading.Thread(target=self.change_scale)

        thread1.start()
        thread2.start()
        thread3.start()
        thread4.start()

        # thread1.join()
        # thread2.join()
        # thread3.join()
        # thread4.join()

    def fire_events(self):
        """
        Thead that implements the synchronization between the threads using Events.
        It loops forever, sleeping for one measure at each loop. It triggers the
        sequencer event at each measure, and the scale based on the
        measuresForScaleChange attribute (the default is a scale change every 4 measures).
        """
        measure_counter = self.measureCount
        while True:
            # one measure sleep
            time.sleep(self.durations['1'])
            print('[measure {}/{}]'.format(measure_counter + 1, self.measuresForScaleChange))

            if measure_counter == 0:
                # triggering a scale change
                self.changeScaleEvent.set()

                # synchronization between play_midi and change_scale threads
                self.changeScaleDoneEvent.clear()

            # increasing the measure counter
            measure_counter = measure_counter + 1
            if measure_counter >= self.measuresForScaleChange:
                measure_counter = 0

            # saving the value of the measure counter as a class attribute
            with self.lock:  # critical section
                self.measureCount = measure_counter
            # critical section

            # triggering the sequencer and the chords
            self.sequencerEvent.set()

    def listen_midi(self):
        """
        Thread implementing a never ending loop, listening for note_on/note_off
        messages from the midiInPort, saving the messages into a buffer.
        When the buffer is full, the messages are moved into the midiNoteQueue.
        """

        # buffer used to store the incoming midi note messages
        midi_buffer = []

        # receiving midi messages
        with mido.open_input(self.midiInPort) as midi_in_port:
            for midi_msg in midi_in_port:
                if midi_msg.type == 'note_on' or 'note_off':
                    # saving the messages in a buffer
                    midi_buffer.append({
                        'msg': midi_msg,
                        'timestamp': time.time()
                    })
                    # print(midi_msg)
                    if len(midi_buffer) >= self.midiBufferLen:
                        # moving the messages from the midiBuffer to the midiNoteQueue
                        # and adding the new notes to the noteBuffer
                        with self.lock:  # critical section
                            for msg in midi_buffer:
                                self.midiNoteQueue.push(msg['msg'].type, msg['msg'].note, msg['timestamp'])
                                self.noteBuffer = self.noteBuffer + self.midiNoteQueue.get_notes()

                        # resetting the buffer
                        midi_buffer = []

                        # triggering the event
                        self.bufferFullEvent.set()

    def play_midi(self):
        notes_markov_chain = markov_chain.MarkovChain()
        rhythm_markov_chain = markov_chain.MarkovChain()
        current_chord = None
        note_input_sequence = []
        rhythmic_input_sequence = []
        generated_sequence_max_length = 10  # TODO: fine tune the value
        note_generated_sequence = []
        midi_generated_sequence = []
        rhythm_generated_sequence = []
        sequencer_input = []
        chord_notes = []

        # waiting for the first measure
        self.bufferFullEvent.wait()

        # synchronization with change_scale thread
        self.changeScaleDoneEvent.wait()

        # initializing all the objects =======
        with self.lock:  # critical section
            # the first scale is also set here
            self.harmonicState.push_notes(self.noteBuffer)
        # end of critical section

        with self.lock:
            current_chord = self.degree_to_chord(self.chordSequence[self.measureCount])

        rhythmic_input_sequence, note_input_sequence = self.parse_midi_notes(current_chord)
        notes_markov_chain.learn(note_input_sequence)
        rhythm_markov_chain.learn(rhythmic_input_sequence)
        # end of initialization ==============

        while True:
            # waiting for one measure
            self.sequencerEvent.wait()
            self.sequencerEvent.clear()

            # synchronization with change_scale thread
            self.changeScaleDoneEvent.wait()

            with self.lock:
                current_chord = self.degree_to_chord(self.chordSequence[self.measureCount])

            # TODO: play the chord

            # parsing the rhythm and the notes
            rhythmic_input_sequence, note_input_sequence = self.parse_midi_notes(current_chord)

            # training the markov chains
            if note_input_sequence and rhythmic_input_sequence:
                notes_markov_chain.learn(note_input_sequence)
                rhythm_markov_chain.learn(rhythmic_input_sequence)

            # generating the new sequences that fits in one measure
            rhythm_generated_sequence = rhythm_markov_chain.generate(generated_sequence_max_length)
            rhythm_generated_sequence = melodically.clip_rhythmic_sequence(rhythmic_input_sequence, 1)
            note_generated_sequence = notes_markov_chain.generate(len(rhythm_generated_sequence))
            midi_generated_sequence = self.generate_midi_sequence(note_generated_sequence, current_chord)

            # TODO: understand why some sequence are empty
            # TODO: play a chord even if the sequence is empty

            # playing the sequencer
            if rhythm_generated_sequence:
                sequencer_input = [{'note': x, 'duration': y} for x, y in
                                   zip(midi_generated_sequence, rhythm_generated_sequence)]
                chord_input = self.generate_midi_chord(current_chord)
                self.sequencer.play(sequencer_input, chord_input)

            print('abstract melody: {}'.format(note_generated_sequence))
            print('rhythmic pattern: {}'.format(rhythm_generated_sequence))
            print('midi notes: {}'.format(midi_generated_sequence))
            print('chord: {}'.format(current_chord))
            print()

    def change_scale(self):
        # markov chain trained on The Beatles chord database
        chords_markov_chain = markov_chain.chord_markov_chain

        # waiting for the midiBuffer to be full
        self.bufferFullEvent.wait()

        while True:
            # waiting for the scale change event
            self.changeScaleEvent.wait()
            self.changeScaleEvent.clear()

            # updating the scale and the chords
            with self.lock:  # critical section
                self.chordSequence = chords_markov_chain.sample(4)
                self.harmonicState.push_notes(self.noteBuffer)
                self.noteBuffer = []
                self.currentScale = self.harmonicState.get_mode_notes()
                print('scale: {}'.format(self.currentScale))
                print('next chords: {}'.format(self.chordSequence))
            # end of critical section

            # synchronization with play_midi thread
            self.changeScaleDoneEvent.set()

    def parse_midi_notes(self, current_chord):
        """
        Parses the note and rhythmic sequence from the midiNoteQueue.

        :param current_chord: chord in melodically notation
        :return: rhythmic_input_sequence, note_input_sequence lists
        """
        rhythmic_input_sequence = []
        note_input_sequence = []
        with self.lock:  # critical section
            notes = self.midiNoteQueue.get_notes()
            rhythmic_input_sequence = melodically.parse_rhythm(self.midiNoteQueue, self.durations)
            note_input_sequence = [melodically.parse_musical_note(note, current_chord) for note in notes]
            self.midiNoteQueue.clear()  # clearing the note queue
        # end of the critical section
        return rhythmic_input_sequence, note_input_sequence

    def generate_midi_sequence(self, note_sequence, chord):
        c_tones = melodically.chord_tones[chord]['c']
        l_tones = melodically.chord_tones[chord]['l']
        notes_not_in_scale = list(set(melodically.musical_notes) - set(c_tones) - set(l_tones))
        result = []
        for note in note_sequence:
            if note == 'c':
                result.append(self.random_pick(c_tones))
            elif note == 'l':
                result.append(self.random_pick(l_tones))
            else:
                result.append(self.random_pick(notes_not_in_scale))

        return result

    def generate_midi_chord(self, chord):
        random_octaves = [random.randint(self.chordOctaveRange[0], self.chordOctaveRange[1]) for i in range(4)]
        return melodically.chord_to_midi(chord, random_octaves)

    def random_pick(self, sequence):
        return melodically.std_to_midi(random.choice(sequence),
                                       random.randint(self.melodyOctaveRange[0], self.melodyOctaveRange[1]))

    def degree_to_chord(self, degree):
        degree_number = degrees.index(degree)
        current_mode = self.harmonicState.currentMode
        root = current_mode['root']
        mode_index = current_mode['mode_index']
        chord = melodically.modes_chords_dict[root][mode_index][degree_number]
        return chord