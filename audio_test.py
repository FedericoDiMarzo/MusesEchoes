from AudioStream import AudioStream
import matplotlib.pyplot as plt
import librosa

if __name__ == '__main__':
    RATE = 44100
    audio_stream = AudioStream(RATE)
    audio = audio_stream.read(1)
    plt.plot(audio)
    plt.show()
    print(len(librosa.feature.chroma_stft(audio)))
