from Improvisor import get_all_modes, note_list, read_midi

if __name__ == '__main__':
    for note in note_list:
        print("modes of " + note + ":")
        mode_list = get_all_modes(note)
        for i in range(len(mode_list)):
            print("current semitone sequence: " + str(i))
            for j, m in enumerate(mode_list[i]):
                print('mode of grade ' + str(j))
                print(m)
            print('\n')
        print('\n\n')

    read_midi('../media/midi/midi1.mid')