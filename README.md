## Muses Echoes

Our creativity is inspired by everything we heard, everything we have listened to. Creativity is an amazing process generated by the ideas of who came before us in history.
It often happens that creativity experiences a block, an interruption, a moment of stalemate; This is where technology comes into play, simulating the most intimate thing there can be during the creative process, providing the artist not merely with support but with a total source of inspiration. Greeks used to have Inspirational Muses. We created this tool to make an inspiring Muse available to the user.

Once your instrument is connected, Muses’echoes will provide the opportunity to be surrounded by rhythms, chords and vocal melodies that will dance together with the musician's creative flow, contributing to an endless inspirational flow.

Muses’s echoes can also be seen as an installation to be placed in a dark room consisting of a screen and speakers that gives a visual and acoustical feedback based upon musical inputs of attenders.
The immersive experience you live inside the room will give you the possibility of interacting with the installation by the instruments placed inside the room.

 ## muses.py
Muses.py is the main class that makes up the Muse's Echoes application. After an object is created passing all the requested parameters to modify the settings, the application can be started calling the start method. The start method will block the execution and spawn the threads needed for the application to work. The fire_event method will than handle the synchronization between the threads.

### Constructor
Can be found in muses.py class. The following are the editable parameters for an easy Muses Echoes customisation:

```midi_in_port```: name of the midi input port

```midi_sequence_out_port```: name of the midi output port for the melody

```midi_chord_out_port```: name of the midi output port for the chords

 ```midi_rhythm_out_port```: name of the midi output port for the rhythm
 
```midi_mapping```: indicates how the modes are mapped to a certain midi channel

```midi_buffer_size```: size of the buffer used to store midi notes before pushing them in the MidiNoteQueue

```osc_ip```: ip string for the osc node receiving information about the scale

```osc_port```: port string the osc node receiving information about the scale

```bpm```: floats indicating the beats per minutes of the performance

```measures_for_scale_change```: positive integer indicating the number of measures for a change of scale

```melody_octave_range```: tuple containing the lowest and the highest octaves used for generating the melodies

```chord_octave_range```: tuple containing the lowest and the highest octaves used for generating the chords

```rhythm_midi_note```: midi note used for the rhythmic sequencer track

```markov_chains_order```: order of the Markov Chains used to generate the melodies

```markov_chains_inertia```: value between ```[0-1]``` used to indicate the influence of old melodies in the learning


## Markow Chains
Muses Echoes implements a Markow chain driven through a database of Beatles songs as an “engine” for the progressive generation of melodies, chords, rhythms.
The database used is that relating to the discography of the musical group The Beatles, thanks to the great variety of tones within the songs and the considerable popularity that these songs have achieved. The generation of rhythms, chords, melodies will therefore have a completely familiar feeling.
The database used can be found at the following link: [http://isophonics.net/content/reference-annotations-beatles](http://isophonics.net/content/reference-annotations-beatles).

The process of creating the customized database comes from a "cleaning" relating to the information relating to the songs that are not necessary for the training of the Markow chains. The processing of the Structural_Segmentation, csv and Chords.csv files was useful. A Python script has been implemented which is useful for extrapolating from these .csv files only what is of interest to us.

The implementation of the Markov Chain was possible thanks to the use of a library provided by [Pomegranate]( https://pomegranate.readthedocs.io/en/latest/MarkovChain.html)

Inside the __main__.py file, Pomegranate gives the possibility to manage two fundamental parameters for the correct functioning of Muses Echoes. The following parameters can be changed as desired based on purely artistic matters.

```python
_markov_chains_order = 3
_markov_chains_inertia = 0.78
```
More precisely, the “Inertia” parameter provides the possibility to totally ignore the old parameters (0.0), or the new parameters (1.0).

The "Order" parameter defines the order of the Markow Chain. It is possible to modify this parameter as desired, taking into account the following factors:
- Goodness of predictions
- Overall latency
An order "3" with an inertia "0.78" generally shows itself as a good compromise.


## Modularity
The design of the system focuses on modularity, i.e. the possibility that the user or artist has to use all the tools available at will, developing personal installations and keeping the level of creativity high.
It is possible to use the Muses Echoes output parameters as you see fit, by implementing different DAWs and programming sounds and rhythms to your liking, or by triggering different musical instruments using the universal MIDI and OSC protocols.
There is also a total modularity of ports. Muses Echoes provides the ability to set names and uses for the ports you prefer.


## Preliminary steps
First of all, make sure to run the
```shell
pip install requirements.txt
```
command in you shell, in order to install all the packages needed for a correct Muse’s Echoes funtioning.

## MIDI set up
Muses Echoes needs 4 MIDI ports in input-output in the following configuration:
- Input Ports: ```python [in]```
- Output Ports: ```python [melody] [chord] [rhythm]```

The input port must necessarily be configured by your DAW in order to be able to send midi notes to Muse's Echoes.

First of all, it is recommended to use the [loopMidi](https://www.tobias-erichsen.de/software/loopmidi.html) software for setting the midi ports. In the following figure you can see the loopMidi software screen in which four virtual Midi ports have been created, called respectively midi_in, midi_melody, midi_chords, midi_rhythm.

 ![image](https://user-images.githubusercontent.com/60785720/123107810-293d3180-d43a-11eb-93cb-714a691745fe.png)
 
Muse's Echoes will change the midi channel on the basis of the modal scale, starting from the Ionic mode (CH 1) up to the Locrian mode (CH 7). This behavior of the software is useful if the user wants to assign a different sound for each mode within, for example, their DAW.

### Selecting the right MIDI ports
Once the __main.py file is launched, go to the terminal and type the following command:
```shell
python -m muses echoes
```
The system will show the position of the midi ports.

```shell
usage: python -m muses_echoes [in] [melodies] [chords] [rhythm]

-----------

midi in ports: ['Launchkey Mini MK3 MIDI 4', 'MIDIIN2 (Launchkey Mini MK3 MID 5', 'loop-chords 2', 'loop-input 0', 'loop-melody 1', 'loop-rhythm 3']
midi out ports: ['Launchkey Mini MK3 MIDI 5', 'MIDIOUT2 (Launchkey Mini MK3 MI 6', 'Microsoft GS Wavetable Synth 0', 'loop-chords 3', 'loop-input 1', 'loop-melody 2', 'loop-rhythm 4']

-----------

[in]: midi in port index used to receive notes
[melodies]: midi out port index used to send notes for the melody
[chords]: midi out port index used to send notes for the chords
[rhythm]: midi out port index used to send notes for the rhythm
```

To set the correct parameter for each midi port it is sufficient to indicate the position of the relative ports shown, starting from the zero value:

```shell
python -m muses_echoes [in] [melody] [chord] [rhythm]
```

In this precise case for example the input needs to be:

```shell
python -m muses_echoes 4 6 4 7
```

When __main__.py is executed, the name of the ports associated with each relative input / output is printed on the terminal. It is therefore possible to check that everything is set correctly.

```shell
selected midi input: loop-input 0
selected midi sequence output: loop-melody 2
selected midi chord output: loop-chords 3
selected midi rhythm output: loop-rhythm 4
```

## OSC Set up
Muses Echoes supports the OSC protocol for sending data. These data can be used for the management of a particular graphic interface through for example the [MadMapper](https://madmapper.com/) software, [Processing](https://processing.org/), [TouchDesigner](https://derivative.ca/), or a [DMX](https://it.wikipedia.org/wiki/Digital_MultipleX) control unit or anything else.
A different value is sent through the OSC protocol each time a scale change occurs.
Inside the __main__.py file there is the area where you can set parameters such as:
- IP address (default: 127.0.0.1)
- UDP port (default: 1337)

```python
_osc_ip = "127.0.0.1"
_osc_port = 1337
```
OSC sends a value every time a change of scale occurs (useful for programming changing visuals)

## Sound Design

there are certain ways to use different modes, in order to produce scales and melodies. One  way to describe or distinguish one mode from another is the **mood** or **feeling** that a certain mode gives to an human being. This comes from how Bright or Dark these modes are. For example, Lydian and Ionian Modes are used in happy and spiritually uplifting music. Mixolydian and Dorian Modes are often used in blues and gospel music. The Aeolian (minor) Mode is defined as melancholy and sad while Phrygian and Locrian Modes are the go-to Modes for scary, dramatic, and otherworldly sounds. [1]
Below we represent a Brightest to Darkest modes chart. It is possible to notice that the more Flats, the Darker the sound:
- Lydian: 1 2 3 #4 5 6 7 (Brightest)
- Ionian: 1 2 3 4 5 6 7
- Mixolydian: 1 2 3 4 5 6 b7
- Dorian: 1 2 b3 4 5 6 b7
- Aeolian: 1 2 b3 4 5 b6 b7
- Phrygian: 1 b2 b3 4 5 b6 b7
- Locrian: 1 b2 b3 4 b5 b6 b7 (Darkest)

[1] For more, read this article: [http://blog.dubspot.com/music-theory-modes/](http://blog.dubspot.com/music-theory-modes/)


### DAW Set up
Here we used the Ableton Live software but it is possible to carry out the same operations with all DAWs / software that support the management of the Midi / OSC protocol.

TODO: END UP CHANNELS DESCRIPTION

![LOOP-IN](https://user-images.githubusercontent.com/60785720/123548930-307c7c00-d767-11eb-8ec0-f04a23335eef.JPG)
![DIRECT-PLAY](https://user-images.githubusercontent.com/60785720/123548929-2fe3e580-d767-11eb-895a-ffd2b0fd991b.JPG)
![MELODY](https://user-images.githubusercontent.com/60785720/123548931-307c7c00-d767-11eb-91ac-224854b8fb90.JPG)
![CHORDS](https://user-images.githubusercontent.com/60785720/123548928-2f4b4f00-d767-11eb-84d8-4208bf31c53a.JPG)
![RHYTHM](https://user-images.githubusercontent.com/60785720/123549132-ea73e800-d767-11eb-8911-a85b66faa848.JPG)
![WHOLE](https://user-images.githubusercontent.com/60785720/123549067-b13b7800-d767-11eb-9eda-d5fac6fb43dd.JPG)


## Touch Designer
Although Muses’ Echoes can be used with many different subsystems for visual renderings, an example application, based on TouchDesigner (https://derivative.ca)  can be found directly in this repository inside the omonimous folder.

In order to run the TouchDesigner project, a version of the software (the free one is compatible with it) should be downloaded and installed from their website at https://derivative.ca/download .
After the software has been installed, the script MusesEchoes.x.toe (where x is the latest version) inside the TouchDesigner folder can be launched.

The visuals will start, presenting a white screen. In order to interact with the animation, the osc and midi settings must be changed. 

For the midi settings, follow “Dialogs/MIDI Device Mapper”, a window showing the midi devices will appear. From this window, after the loopback ports have been setted up as explained in the previous section, check that the devices shown are the same as the ones in the figure below.

FOTO_MIDI

The TouchDesigner implementation supports only major and minor clusters of modes in the midi channels 1 (I-IV-V modes) and 2 (II-III-VI-VII modes). To reflect this mapping, the following setting should be changed inside the ``__main__.py`` script:

```python
_midi_mapping = [1, 2, 2, 1, 1, 2, 2]
```

Regarding the osc settings, the default port 1337 is already configured, if you want to change this setting search the osc dat block in figure (top left of the network), and modify its setting reflecting the one inside the ``__main__.py`` script.

FOTO_OSC

inside the const dat block named “parameters” (top left of the network) other settings can be modified, affecting the visuals, such as the midi note extensions of the various midi instruments, the size of the rendered notes, the vertical speed, etc..

FOTO_PARAMETERS

The last change that you should do before enjoying the installation, regards the colours of the notes for each instrument. The three VEDERE_NOME top blocks contain a reset button that can be pressed for a random palette generation. Keep resetting the palettes until you find the best for your tastes.

GIF_COLORS

