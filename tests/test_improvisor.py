from Improvisor import get_all_modes, note_list

if __name__ == '__main__':
    for note in note_list:
        print("modes of " + note + ":")
        mode_list = get_all_modes(note)
        for i, m in enumerate(mode_list[0]):
            print('mode of grade ' + str(i))
            print(m)
        print('\n\n')