from AudioStream import AudioStream
from Sequencer import Sequencer
import time
import matplotlib.pyplot as plt
import librosa

if __name__ == '__main__':
    RATE = 44100
    audio_stream = AudioStream(RATE)
    audio = audio_stream.read(1)
    # plt.plot(audio)
    # plt.show()
    # print(len(librosa.feature.chroma_stft(audio)))

    # testing the sequencer
    sequencer = Sequencer()
    sequencer.start()
    time.sleep(7.9)
    sequencer.set_bpm(120)
    time.sleep(7.9)
    sequencer.set_bpm(240)
    time.sleep(7.9)

    sequencer.close()
    audio_stream.close()
    while True:
        pass
