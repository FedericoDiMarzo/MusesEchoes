# MUSES ECHOES

## INTRO
TODO

## muses.py
Muses.py is the main class that makes up the Muse's Echoes application. After an object is created passing all the requested parameters to modify the settings, the application can be started calling the start method. The start method will block the execution and spawn the threads needed for the application to work. The fire_event method will than handle the synchronization between the threads.

## MARKOW CHAIN

TODO


## Modularity
We have focused a lot on modularity, i.e. the possibility that the user or artist has to use all the tools available at will, developing personal installations and keeping the level of creativity high.
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
![image](https://user-images.githubusercontent.com/60785720/123108244-8b963200-d43a-11eb-909b-736f3f743d38.png)

To set the correct parameter for each midi port it is sufficient to indicate the position of the relative ports shown, starting from the zero value:
```shell
python -m muses_echoes [in] [melody] [chord] [rhythm]
```
In this case we should enter:
```shell
python -m muses_echoes 4 6 4 7
```

When __main__.py is executed, the name of the ports associated with each relative input / output is printed on the terminal. It is therefore possible to check that everything is set correctly.

![image](https://user-images.githubusercontent.com/60785720/123108596-d6b04500-d43a-11eb-9d1e-40c9ff62f410.png)

## OSC Set up
Muses Echoes supports the OSC protocol for sending data. These data can be used for the management of a particular graphic interface through for example the [MadMapper](https://madmapper.com/) software, [Processing](https://processing.org/), [TouchDesigner](https://derivative.ca/), or a [DMX](https://it.wikipedia.org/wiki/Digital_MultipleX) control unit or anything else.
A different value is sent through the OSC protocol each time a scale change occurs.
Inside the __main__.py file there is the area where you can set parameters such as:
- IP address (default: 127.0.0.1)
- UDP port (default: 1337)

![image](https://user-images.githubusercontent.com/60785720/123109050-3575be80-d43b-11eb-991f-6007df7ec983.png)

## DAW Set up
Here we used the Ableton Live software but it is possible to carry out the same operations with all DAWs / software that support the management of the Midi / OSC protocol.

TODO

## SOUND DESIGN

TODO

