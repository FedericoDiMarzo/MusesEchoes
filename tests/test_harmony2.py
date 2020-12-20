from harmony import get_all_modes, note_std_list, harmonic_affinities, get_root

# test for harmonic_affinities
if __name__ == '__main__':
    inputs = [
        ['C', 'D', 'E', 'F', 'G', 'A', 'B', 'C', 'C'],
        ['C', 'D', 'D#', 'F', 'G', 'A', 'A#', 'C', 'C'],
        ['C', 'D', 'D#', 'F', 'G', 'G#', 'A#', 'C', 'C'],
        ['D', 'D', 'E', 'F', 'G', 'A', 'A#', 'C', 'D'],
        ['D', 'D', 'E', 'F#', 'G', 'A', 'B', 'C', 'D']
    ]

    for x in inputs:
        root = get_root(x)
        modes = get_all_modes(root)
        affinities = harmonic_affinities(modes, x)

        mode_signature_index = affinities.index(max(affinities))
        tmp = affinities[mode_signature_index]
        mode_index = tmp.index(max(tmp))

        print('input:' + str(x))
        print('root note:' + root)
        print('mode indices: ' + str(mode_signature_index) + " " + str(mode_index) + '\n\n------------')
