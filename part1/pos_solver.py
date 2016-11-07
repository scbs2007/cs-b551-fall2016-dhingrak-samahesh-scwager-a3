###################################
# CS B551 Fall 2016, Assignment #3
#
# Your names and user ids: Karun Dhingra, Sanna Wager, Saurav Maheshwary (dhingrak, scwager, samahesh)
#
# (Based on skeleton code by D. Crandall)
#

'''
(1) a description of how you formulated the problem, including precisely defining the abstractions (e.g. HMM formulation); 
  part 1: P(W|S), P(Si+1|Si), P(S) has been calculated and stored in dictionaries.
  part 2: This dealt with the implementation of the Simplified Bayes Net. Here we maximize depending on the P(W|S) * P(S).
  part 3: This dealt with the implementation of the HMM. The HMM was built exactly as given in the pdf. We are using the probabilities
  from the first step for calculations and have used a 2 dimensional matrix to implement the Viterbi Algorithm. The rows of the matrix correspond
  to each word of the sequence and the columns correspond to all possible Pos of a particular word. Then after building the whole matrix with tuples
  of the form (maxProbability, pos). e back track starting from the last row.
  part 4: This dealt with the implementation of the complex Bayes Net. We have implemented the Forward Algorithm to solve it.
  For finding the pos of si+3 we take into consideration all possible transitions from si+2 and si and maximize it.
  
  Result Obtained for given bc.test file after training on the given bc.train file
  ==> So far scored 2000 sentences with 29442 words.
                   Words correct:     Sentences correct:
   0. Ground truth:      100.00%              100.00%
     1. Simplified:       94.37%               49.75%
            2. HMM:       96.11%               60.95%
        3. Complex:       39.19%                0.15%
  ----

(2) 
The program has been divided into many files:
1. trainingProbabilities.py deals with all the Probability calculations and stores P(W|S), P(Si+1|Si), P(Si+2|Si), P(S) values as Counter() variables
2. complexB.py deals with the implementation of the complex bayes net
3. simplified.py deals with the implementation of the naive bayes net
4. hmm.py deals with the implementation of Viterbi
We have also modified the label.py and pos_solver.py files to do the implementation of the posterior probs.

(3) 
It was difficult choosing the probability of a word that was not seen in the training data.
We assign the pos of an unseen word based on the suffix of that word. We have used common suffixes in the English language which tell us the pos. They
were taken from:
        # http://southcentral.edu/images/departments/ASC/documents/Suffixes_that_Indicate_Part_of_Speech_2.pdf
        # https://docs.google.com/document/d/1nxRkGUUmVH2vN2hp39yiMnnBdwo5wqv9dkr4cLn4DMo/edit

We assign the probability of 0.1/ total number of words in the model to P(thatWord| the POS predicted), and dynamically update the model in the hopes of getting better
results for HMM and complex.

The transition probabilities have been smoothed by using Laplace Smoothing. We increase the count of all transitions of all the pos from the training data by 1,
before calculating the transition probabilities.

'''

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
    def posterior(self, sentence, label, algo):
        #print "POSTERIOR: ", sentence, label, algo
        posterior = 0
        pWgivenS = 0
        for i in range(len(sentence)):
            #print i, sentence[i], label[i], self.probObj.probWordGivenPos[sentence[i] + '|' + label[i]], self.probObj.probPos[label[i]]
            #print algo
            if 'Simplified' in algo:
                pWgivenS = self.probObj.probWordGivenPos[sentence[i]+'|'+label[i]]
                #print "PW|S", pWgivenS
            elif 'HMM' in algo:
                #print "Value: ", self.probObj.hmmMarginal[sentence[i]+'|'+ label[i]]
                pWgivenS = self.probObj.hmmMarginal[sentence[i]+'|'+ label[i]]
                
                #print "PW|S", pWgivenS
            elif 'Complex' in algo:
                pWgivenS = self.probObj.complexMarginal[sentence[i]+'|'+ label[i]]
                #return 0
            else:
                return 0
                #pWgivenS = 1
            pWgivenS = 0.1 / self.probObj.countOfWords if pWgivenS == 0 else pWgivenS
            #print pWgivenS, self.probObj.probPos[label[i]]
            posterior += math.log(pWgivenS)#*self.probObj.probPos[label[i]])
        #print "POSTERIOR: ", posterior
        return posterior

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
        return complexB.findPosComplex(self.probObj, sentence)
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

