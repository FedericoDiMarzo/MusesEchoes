from harmony import get_all_modes, note_std_list, harmonic_affinities, get_root

# test for harmonic_affinities
if __name__ == '__main__':
    inputs = [
        ['C', 'D', 'E', 'F', 'G', 'A', 'B', 'C', 'C', 'C'],
        ['C', 'D', 'D#', 'F', 'G', 'A', 'A#', 'C', 'C'],
        ['C', 'D', 'D#', 'F', 'G', 'G#', 'A#', 'C', 'C'],
        ['D', 'D', 'E', 'F', 'G', 'A', 'A#', 'C', 'D'],
        ['D', 'D', 'E', 'F#', 'G', 'A', 'B', 'C', 'D']
    ]

    for x in inputs:
        root = get_root(x)
        modes = get_all_modes(root)
        affinities = harmonic_affinities(modes, x)

        i = affinities.index(max(affinities))
        tmp = affinities[i]
        j = tmp.index(max(tmp))

        print('input:' + str(x))
        print('root note:' + root)
        print('mode indices: ' + str(i) + " " + str(j) + '\n\n------------')
        print('affinity: ' + str(affinities[i][j]))
