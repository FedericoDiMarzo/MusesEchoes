from sequencer import get_scale_from_mode
from harmony import mode_signatures, note_std_list

if __name__ == '__main__':

    for signature in mode_signatures:
        for index in range(7):
            print(
                'mode family signature: {}'.format(signature),
                'mode_index: {}'.format(index),
                'scale: {}'.format(get_scale_from_mode(signature, index)),
                '',
                sep='\n'
            )
