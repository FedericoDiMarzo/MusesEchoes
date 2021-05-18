import mido
import sys
import melodically
import markov_chains
import threading
from pythonosc.udp_client import SimpleUDPClient
import json
import time
import random

"""
Change these variables to easily modify the
settings of the application.
"""
_osc_ip = "127.0.0.1"
_osc_port = 1337
_midi_buffer_size = 10
_bpm = 74
_measures_for_scale_change = 4


class MuseEchoes:
    def __init__(self, midi_in_port, midi_buffer_size=10,
                 osc_ip="127.0.0.1", osc_port=1337,
                 bpm=74, measures_for_scale_change=4):

        # lock used to protect the critical sections
        self.lock = threading.Lock()

        # event triggered when a scale must be changed
        self.changeScaleEvent = threading.Event()

        # event triggered when the sequencer should execute a new melody
        self.sequencerEvent = threading.Event()

        # event triggered when the midi buffer is full
        self.bufferFullEvent = threading.Event()

        # name of the midi in port
        self.midiInPort = midi_in_port

        # ip for the osc protocol
        self.oscIp = osc_ip

        # port for the osc protocol
        self.oscPort = osc_port

        # length of the midi buffer used for the input
        self.midiBufferLen = midi_buffer_size

        # used to buffer the notes in std notation used for the harmonicState
        self.noteBuffer = []

        # setting up OSC
        self.oscClient = SimpleUDPClient(osc_ip, osc_port)

        # midi note queue shared between the threads
        self.midiNoteQueue = melodically.MidiNoteQueue()

        # used to change the scale
        self.harmonicState = melodically.HarmonicState(buffer_size=self.midiBufferLen * 3)  # TODO: fine tune this value

        # current modal scale
        self.currentScale = []

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
        measure_counter = 0
        while True:
            # one measure sleep
            time.sleep(self.durations['1'])
            print('[measure {}/{}]'.format(measure_counter + 1, self.measuresForScaleChange))

            # triggering the sequencer and the chords
            self.sequencerEvent.set()

            # increasing the measure count
            measure_counter = measure_counter + 1

            if measure_counter >= self.measuresForScaleChange:
                # TODO: change scale at measure 1 not 4
                # triggering a scale change
                self.changeScaleEvent.set()

                # resetting the counter
                measure_counter = 0

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
        notes_markov_chain = markov_chains.MarkovChain()
        rhythm_markov_chain = markov_chains.MarkovChain()
        current_chord = 'CM'  # TODO: use the beatles markov chain to change the chord
        note_input_sequence = []
        rhythmic_input_sequence = []
        generated_sequence_max_length = 8  # TODO: fine tune the value
        note_generated_sequence = []
        rhythmic_generated_sequence = []

        # the first training is done here, to avoid empty markov chains
        self.bufferFullEvent.wait()
        self.bufferFullEvent.clear()

        with self.lock:  # critical section
            # the first scale is also set here
            self.harmonicState.push_notes(self.noteBuffer)
        # end of critical section

        rhythmic_input_sequence, note_input_sequence = self.parse_midi_notes(current_chord)
        notes_markov_chain.learn(note_input_sequence)
        rhythm_markov_chain.learn(rhythmic_input_sequence)

        while True:
            # waiting for one measure
            self.sequencerEvent.wait()
            self.sequencerEvent.clear()

            # TODO: change the chord
            # TODO: play the chord
            # TODO: synchronize with the scale change

            # parsing the rhythm and the notes
            rhythmic_input_sequence, note_input_sequence = self.parse_midi_notes(current_chord)

            # training the markov chains
            if note_input_sequence:
                notes_markov_chain.learn(note_input_sequence)
            if rhythmic_input_sequence:
                rhythm_markov_chain.learn(rhythmic_input_sequence)

            # generating the new sequences that fits in one measure
            rhythmic_generated_sequence = rhythm_markov_chain.generate(generated_sequence_max_length)
            # TODO: debug
            rhythmic_generated_sequence = melodically.clip_rhythmic_sequence(rhythmic_input_sequence, 1)
            note_generated_sequence = notes_markov_chain.generate(len(rhythmic_generated_sequence))
            print(note_generated_sequence)
            print(rhythmic_generated_sequence)
            print()

            # TODO: play the sequence with the sequencer

    def change_scale(self):
        while True:
            # waiting for the scale change event
            self.changeScaleEvent.wait()
            self.changeScaleEvent.clear()
            # updating the scale
            with self.lock:  # critical section
                self.harmonicState.push_notes(self.noteBuffer)
                self.noteBuffer = []
                self.currentScale = self.harmonicState.get_mode_notes()
                print(self.currentScale)
            # end of critical section

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


if __name__ == '__main__':

    # =========================================
    # command line feedback for the users
    # =========================================
    midi_input_names = mido.get_input_names()

    if len(sys.argv) <= 1:
        print('usage: python -m midi_server.py midi_port\n',
              'midi ports: {}'.format(midi_input_names),
              sep='\n')
        exit(-1)

    midi_index = int(sys.argv[1])

    print('selected midi input: {}'.format(midi_input_names[midi_index]),
          '',
          sep='\n')
    # =========================================
    # =========================================

    # creating and starting the multi-threaded application
    midiServer = MuseEchoes(
        midi_in_port=midi_input_names[midi_index],
        osc_ip=_osc_ip,
        osc_port=_osc_port,
        midi_buffer_size=_midi_buffer_size,
        bpm=_bpm,
        measures_for_scale_change=_measures_for_scale_change,
    )
    midiServer.start()
