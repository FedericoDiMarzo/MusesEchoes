import pomegranate as pg

prefixes = ['c', 'l', 'x', 'r']
suffixes = ['1', '2', '4', '4t', '4dot', '8', '8t', '16', '16t']
all_symbols = [x + y for x in prefixes for y in suffixes]


class AbstractMelodyMarkovChain:
    def __init__(self, order=3):
        # initializing the markov chain with all the symbols
        self.markovChain = pg.MarkovChain.from_samples(all_symbols, k=order)

        # value between 0 and 1 that indicates how old melodies still
        # influence the probabilities of the markov chain
        self.keepOldMelodies = 0.7

        # flag to indicate if the first melody has already been learned
        self.isTheFirstMelody = True

    def learn_melody(self, melody):
        if self.isTheFirstMelody:
            self.markovChain.fit(melody, inertia=0)
        else:
            self.markovChain.fit(melody, inertia=self.keepOldMelodies)

    def generate_new_melody(self, length):
        return self.markovChain.sample(length)
