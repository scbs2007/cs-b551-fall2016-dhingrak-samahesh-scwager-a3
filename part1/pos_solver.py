###################################
# CS B551 Fall 2016, Assignment #3
#
# Your names and user ids: Karun Dhingra, Sanna Wager, Saurav Maheshwary (dhingrak, scwager, samahesh)
#
# (Based on skeleton code by D. Crandall)
#
#
####
# Put your report here!!
####
#
from trainingProbabilities import TrainingProbs
import simplified
import hmm
import complexB
import random
import math

# We've set up a suggested code structure, but feel free to change it. Just
# make sure your code still works with the label.py and pos_scorer.py code
# that we've supplied.
#
class Solver:
    
    def __init__(self):
        self.probObj = TrainingProbs() 
    
    # Calculate the log of the posterior probability of a given sentence
    # with a given part-of-speech labeling
    #
    def posterior(self, sentence, label):
        return 0

    # Do the training!
    #
    def train(self, data):
        self.probObj.train(data)

    # Functions for each algorithm.
    #
    def simplified(self, sentence):
        result = simplified.findPosSimplified(self.probObj, sentence)
        #print result
        return result
        #return [ [ [ "noun" ] * len(sentence)], [[0] * len(sentence),] ]

    def hmm(self, sentence):
        return hmm.findPosHmm(self.probObj, sentence)
        #return [ [ [ "noun" ] * len(sentence)], [] ]

    def complex(self, sentence):
        #return complexB.findPosComplex(self.probObj, sentence)
        return [ [ [ "noun" ] * len(sentence)], [[0] * len(sentence),] ]


    # This solve() method is called by label.py, so you should keep the interface the
    #  same, but you can change the code itself. 
    # It's supposed to return a list with two elements:
    #
    #  - The first element is a list of part-of-speech labelings of the sentence.
    #    Each of these is a list, one part of speech per word of the sentence.
    #
    #  - The second element is a list of probabilities, one per word. This is
    #    only needed for simplified() and complex() and is the marginal probability for each word.
    #
    def solve(self, algo, sentence):
        if algo == "Simplified":
            return self.simplified(sentence)
        elif algo == "HMM":
            return self.hmm(sentence)
        elif algo == "Complex":
            return self.complex(sentence)
        else:
            print "Unknown algo!"

