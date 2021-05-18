import pomegranate as pg

# prefixes = ['c', 'l', 'x', 'r']
# suffixes = ['1', '2', '4', '4t', '4dot', '8', '8t', '16', '16t']
# all_symbols = [x + y for x in prefixes for y in suffixes]


class MarkovChain:
    """
    Adaptor class that wraps the pomegranate
    implementation of a Markov Chain.
    """

    def __init__(self, order=3):
        # markov chain reference
        self.markovChain = None

        # value between 0 and 1 that indicates how old melodies still
        # influence the probabilities of the markov chain
        self.keepOldMelodies = 0.7

        # flag to indicate if the first melody has already been learned
        self.isTheFirstMelody = True

    def learn(self, sequence):
        """
        Learn from a new symbol input sequence.

        :param sequence: list of symbols
        """
        if self.isTheFirstMelody:
            self.markovChain = pg.MarkovChain.from_samples([sequence])
        else:
            self.markovChain.fit([sequence], inertia=self.keepOldMelodies)

    def generate(self, length):
        """
        Generate a new sequence of symbols of a certain length.

        :param length: length of the generated sequence
        :return: list of symbols
        """
        return self.markovChain.sample(length)
