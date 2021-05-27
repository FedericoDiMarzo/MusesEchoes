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
    """
    This class implements the Muses' Echoes application.
    After an object is created passing all the requested parameters to modify
    the settings, the application can be started calling the start method.
    The start method will block the execution and spawn the threads needed
    for the application to work. The fire_event method will than handle the
    synchronization between the threads.

    Muses' Echoes is an application that interacts with other
    subsystem through the midi and osc protocols.
    The midi setup is based on midi loop ports, that allow the communication
    between the python interpreter and a midi host like a DAW.
    A first midi port must be configured in the DAW to send midi notes to
    Muses' Echoes, this port will capture the melodies from the users.
    Two additional midi ports can be configured in the DAW to control
    the sound generation of the melody and of the chords. Muses' Echoes
    will change the midi channel depending on the modal scale, starting
    from the Ionic mode (channel 1) to the Locrian mode (channel 7); this
    mechanism can be used to vary the instruments in the DAW depending on the
    channel (and thus on the mode), to variate the soundscape.
    The modal variation is also sent through the osc protocol, in order to
    control additional subsystem that could, for example, generate visual contents
    based on the scale that is been playing.
    """

    def __init__(self, midi_in_port,
                 midi_sequence_out_port, midi_chord_out_port,
                 midi_mapping=[1, 2, 3, 4, 5, 6, 7],
                 midi_buffer_size=10,
                 osc_ip="127.0.0.1", osc_port=1337,
                 bpm=74, measures_for_scale_change=4,
                 melody_octave_range=(4, 6),
                 chord_octave_range=(2, 5),
                 markov_chains_order=3,
                 markov_chains_inertia=0.7):
        """
        Constructor.

        :param midi_in_port: name of the midi input port
        :param midi_sequence_out_port: name of the midi output port for the melody
        :param midi_chord_out_port: name of the midi output port for the chords
        :param midi_mapping: indicates how the modes are mapped to a certain midi channel
        :param midi_buffer_size: size of the buffer used to store midi notes before pushing them in the MidiNoteQueue
        :param osc_ip: ip string for the osc node receiving information about the scale
        :param osc_port: port string the osc node receiving information about the scale
        :param bpm: floats indicating the beats per minutes of the performance
        :param measures_for_scale_change: positive integer indicating the number of measures for a change of scale
        :param melody_octave_range: tuple containing the lowest and the highest octaves used for generating the melodies
        :param chord_octave_range: tuple containing the lowest and the highest octaves used for generating the chords
        :param markov_chains_order: order of the Markov Chains used to generate the melodies
        :param markov_chains_inertia: value between [0-1] used to indicate the influence of old melodies in the learning
        """

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

        # mode to midi channel mapping
        self.midiMapping = midi_mapping
        self.midiMappingIndex = 0

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
        self.harmonicState = melodically.HarmonicState(buffer_size=self.midiBufferLen * 3)  # TODO: fine tune this value (Andre)

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

        # order and inertia parameters of the markov chains
        self.markovChainsOrder = markov_chains_order
        self.markovChainsInertia = markov_chains_inertia

    def start(self):
        """
        Starts all the threads of the application
        """

        # spawning the threads
        thread1 = threading.Thread(target=self.listen_midi)
        thread2 = threading.Thread(target=self.fire_events)
        thread3 = threading.Thread(target=self.play_midi)
        thread4 = threading.Thread(target=self.change_scale)

        # starting the threads
        thread1.start()
        thread2.start()
        thread3.start()
        thread4.start()

        # joining the threads
        thread1.join()
        thread2.join()
        thread3.join()
        thread4.join()

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
        """
        This thread generates a melody using two Markov Chains, one for the
        note sequence and one for the rhythmic sequence. It then uses a combination
        of these sequences, and the current chord as an input for the midi sequencer.
        """

        # =================================================
        # Local variables
        # =================================================

        # markov chain used for generate a note sequence
        notes_markov_chain = markov_chain.MarkovChain(order=self.markovChainsOrder, inertia=self.markovChainsInertia)

        # markov chain used to generate the rhythmic sequence
        rhythm_markov_chain = markov_chain.MarkovChain(order=self.markovChainsOrder, inertia=self.markovChainsInertia)

        # current chord to be played in melodically notation
        current_chord = None

        # sequence of input notes in std notation
        note_input_sequence = []

        # sequence of rhythmic symbols
        rhythmic_input_sequence = []

        # max length of the generated sequences
        generated_sequence_max_length = 10

        # generated sequence for the notes in std notation
        note_generated_sequence = []

        # generated sequence for the notes as midi values
        midi_generated_sequence = []

        # generated sequence for the rhythmic symbols
        rhythm_generated_sequence = []

        # sequence of note in the format accepted by the sequencer
        sequencer_input = []

        # midi notes to be played by the sequencer for the chord generation
        chord_input = []

        # end of local variables =============================

        # =================================================
        # Initialization
        # =================================================

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
        # end of initialization ==============================

        # =================================================
        # Sequence and chord generation loop
        # =================================================
        while True:
            # waiting for one measure
            self.sequencerEvent.wait()
            self.sequencerEvent.clear()

            # synchronization with change_scale thread
            self.changeScaleDoneEvent.wait()

            # getting the current chord and midi channel
            with self.lock:  # critical section
                current_chord = self.degree_to_chord(self.chordSequence[self.measureCount])
                midi_channel = self.midiMapping[self.midiMappingIndex]
            # end of critical section

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

            # playing the sequencer
            if rhythm_generated_sequence:
                sequencer_input = [{'note': x, 'duration': y} for x, y in
                                   zip(midi_generated_sequence, rhythm_generated_sequence)]
                chord_input = self.generate_midi_chord(current_chord)
                self.sequencer.play(sequencer_input, chord_input, midi_channel)

            # logging to the console
            print('abstract melody: {}'.format(note_generated_sequence))
            print('rhythmic pattern: {}'.format(rhythm_generated_sequence))
            print('midi notes: {}'.format(midi_generated_sequence))
            print('chord: {}'.format(current_chord))
            print()

        # end of the loop ====================================

    def change_scale(self):
        """
        Thread used to update the harmonic frame of the execution.
        It updates the harmonicState and generates a chord succession
        using a Markov chain trained on the beatles chord database.
        """
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
                self.chordSequence = chords_markov_chain.sample(self.measuresForScaleChange)
                self.harmonicState.push_notes(self.noteBuffer)
                self.noteBuffer = []
                self.currentScale = self.harmonicState.get_mode_notes()
                self.midiMappingIndex = self.harmonicState.currentMode['mode_index']
                print('scale: {}'.format(self.currentScale))
                print('next chords: {}'.format(self.chordSequence))
                print('midi channel: {}'.format(self.midiMapping[self.midiMappingIndex]))
            # end of critical section

            # synchronization with play_midi thread
            self.changeScaleDoneEvent.set()

    def parse_midi_notes(self, current_chord):
        """
        Utility method used to parse the note and rhythmic sequences
        from the midiNoteQueue.

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
        """
        Utility method used to generate a midi sequence from an abstract
        melody and an input chord.

        :param note_sequence: abstract notes sequence
        :param chord: chord in melodically notation
        :return: midi sequence of the melody
        """
        c_tones = melodically.chord_tones[chord]['c']
        l_tones = melodically.chord_tones[chord]['l']
        result = []
        for note in note_sequence:
            if note == 'c':  # chord tone
                result.append(self.midi_random_note_pick(c_tones))
            elif note == 'l':  # color tone
                result.append(self.midi_random_note_pick(l_tones))
            else:  # random tone
                result.append(self.midi_random_note_pick(melodically.musical_notes))

        return result

    def generate_midi_chord(self, chord):
        """
        Utility method used to Generate a list of midi notes
         composing a chord with a random voicing.

        :param chord: chord in melodically notation
        :return: list of notes composing the chord
        """
        random_octaves = [random.randint(self.chordOctaveRange[0], self.chordOctaveRange[1]) for i in range(4)]
        return melodically.chord_to_midi(chord, random_octaves)

    def midi_random_note_pick(self, note_collection):
        """
        Utility method used to pick a random note from a note_collection,
        generating a midi note between the octaves specified in the
        melodyOctaveRange method.

        :param note_collection: list of notes in std notation
        :return: midi value of the picked note
        """
        return melodically.std_to_midi(random.choice(note_collection),
                                       random.randint(self.melodyOctaveRange[0], self.melodyOctaveRange[1]))

    def degree_to_chord(self, degree):
        """
        Utility method that returns a chord in melodically notation
        from a chord degree.

        :param degree: chord degree in roman notation
        :return: chord in melodically notation
        """
        degree_number = degrees.index(degree)
        current_mode = self.harmonicState.currentMode
        root = current_mode['root']
        mode_index = current_mode['mode_index']
        chord = melodically.modes_chords_dict[root][mode_index][degree_number]
        return chord
