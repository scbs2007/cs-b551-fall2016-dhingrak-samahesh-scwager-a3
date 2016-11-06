from __future__ import division
from collections import Counter
#import cProfile, pstats, StringIO

class TrainingProbs:
    
    def __init__(self):
        # For Predicting POS of words not present in Training data - using suffixes of words
        # http://southcentral.edu/images/departments/ASC/documents/Suffixes_that_Indicate_Part_of_Speech_2.pdf
        # https://docs.google.com/document/d/1nxRkGUUmVH2vN2hp39yiMnnBdwo5wqv9dkr4cLn4DMo/edit
        
        # Most Common Suffixes
        self.suffix = ['algia', 'ician', 'sion', 'tion', 'ance', 'ence', 'hood', 'ment', 'ness', 'like', 'logy', 'able', 'ible', 'ancy',\
                        'ian', 'ion', 'acy', 'ade', 'age', 'ism', 'ist', 'ity', 'ful', 'ish', 'ous', 'ate', 'ify', 'ize', 'ing', 'ary', 'ery', 'ory',\
                        'ar', 'an', 'ant', 'dom', 'ee', 'or', 'er', 'ic', 'cy', 'al', 'ly', 'en', 'ed', 'y', "'s"]
        
        # Most Common Suffixes with their POSs
        self.suffixAndPos = ['algia|noun', 'ician|noun', 'sion|noun', 'tion|noun', 'ance|noun', 'ancy|noun', 'logy|noun', \
                            'ence|noun', 'hood|noun', 'ment|noun', 'ness|noun', 'like|adj', 'able|adj', 'ible|adj', \
                            'ary|noun', 'ery|noun', 'ory|noun', 'ary|adj', 'ery|adj', 'ory|adj', 'ion|noun', 'acy|noun', \
                            'ade|noun', 'ate|noun', 'age|noun', 'ant|noun', 'ism|noun', 'ist|noun', 'ity|noun', 'dom|noun',\
                            'ful|adj', 'ian|adj', 'ish|adj', 'ous|adj', 'ate|adj', 'ade|verb', 'ify|verb', 'ing|verb', 'ate|verb', 'ize|verb', \
                            'ar|noun', 'al|noun', 'or|noun', 'cy|noun', 'ee|noun', 'er|noun', 'an|adj', 'ic|adj', 'al|adj', 'ly|adv', 'ly|adj', \
                            'en|verb', 'ed|verb', "'s|noun", 'y|noun', 'y|adj']
        
        self.probSuffixPos = Counter() # Probability of word with suffix being a pos. eg: P of word with suffix 'sion' being a 'noun'
        self.probPos = Counter() # P(S)
        self.probPosGivenPos = Counter() # P(Si+1|Si)
        self.probWordGivenPos = Counter() # P(W|S)
        self.countOfPos = 0 # total number of Pos in training data
        self.countOfWords = 0# Total number of words
        self.delimit = '|'
        self.numberOfSentences = 0
        self.startOfSentence = '#SW#'

    # Check if a word has a suffix that we need
    def checkSuffix(self, word):
        for entry in self.suffix:
            if word.endswith(entry):
                return entry
        return None

    # Check if a given suffix|pos combination is present in our list
    def checkPos(self, suffix, pos):
        suffixPos = suffix + '|' + pos
        if suffixPos in self.suffixAndPos:
            return suffixPos
        return None
        
    # Check if word is present in trained Model
    def checkWordPresent(self, word):
        for entry in self.probWordGivenPos.keys():
            if entry.startswith(word):
                return True
        return False
        
    # Check if word contains digit
    def containsDigit(self, word):
        for ch in word:
            if ch.isdigit():
                return True
        return False

    # Smoothing Transition Probabilities
    def smoothing(self):
        allPos = self.probPos.keys()
        for currentPos in allPos:
            self.probPosGivenPos[currentPos + self.delimit + self.startOfSentence] += 1
            self.probPos[currentPos] += 1
            self.countOfPos += 1
            for previousPos in allPos:
                self.probPosGivenPos[currentPos + self.delimit + previousPos] += 1
                self.probPos[previousPos] += 1
                self.probPos[currentPos] += 1
                self.countOfPos += 2

    # TODO: Update model to reflect unkown word that was found
    def updateModel(self, word, pos):
        self.countOfWords += 1
        query = word + self.delimit + pos
        self.probWordGivenPos[query] = 1/self.countOfWords
	return self.probWordGivenPos[query]
        
    # Training the Model
    def train(self, data):
        #pr = cProfile.Profile()
        #pr.enable()

        for line in data:
            allWordsInLine = line[0]
            allPosInLine = line[1]
            
            self.numberOfSentences += 1
            self.probPosGivenPos[allPosInLine[0] + self.delimit + self.startOfSentence] += 1
            previousPos = ""
            
            for index in range(len(allWordsInLine)):
                word = allWordsInLine[index]
                pos = allPosInLine[index]
                
                # Adding count for <Prefix>|<POS>
                suffixPresent = self.checkSuffix(word) # Check if word has the prefix and pos that we are searching for
                if suffixPresent != None:
                    suffixPos = self.checkPos(suffixPresent, pos)
                    self.probSuffixPos[suffixPresent + '|' + pos] += 1
                
                self.countOfPos += 1

                # Increasing Count of POS found
                self.probPos[pos] += 1
                
                # Increasing count of words
                self.countOfWords += 1

                # Increasing Count of <word>|<pos> found
                self.probWordGivenPos[word + self.delimit + pos] += 1
                
                if previousPos:
                     self.probPosGivenPos[pos + self.delimit + previousPos] += 1
                previousPos = pos

        self.smoothing()
        self.calculateWordProb()
        self.calculateTransitionProb()
        self.calculatePosProb()
        #print "Suffix and POS: "
        #for i in self.suffixAndPos:
        #    print i, self.probSuffixPos[i]
        #pr.disable()
        #s = StringIO.StringIO()
        #sortby = 'cumulative'
        #ps = pstats.Stats(pr,stream=s).sort_stats(sortby)
        #ps.print_stats()
        #print "Timing: ", s.getvalue()
    
    # Calculate P(S)
    def calculatePosProb(self):
        for entry in self.probPos.keys():
            self.probPos[entry] /= self.countOfPos
            #print "POS: entry: ", entry, self.probPos[entry]

    # Calculate P(W|S)
    def calculateWordProb(self):
        for entry in self.probWordGivenPos.keys():
            self.probWordGivenPos[entry] /= self.probPos[entry.split(self.delimit)[1]]
            #print "Word: entry", entry, self.probWordGivenPos[entry]

    # Calculate P(Si+1 | Si) - Transition Probability
    def calculateTransitionProb(self):
        for entry in self.probPosGivenPos.keys():
            pos = entry.split(self.delimit)
            if pos[1] == self.startOfSentence:
                self.probPosGivenPos[entry] /= self.numberOfSentences
            else:
                self.probPosGivenPos[entry] /= self.probPos[pos[0]]
            #print "Transition Probabilities for entry: ", entry, self.probPosGivenPos[entry]

    def getProbNextPosGivenPrevPos(self, prevPos, presentPos):
        return self.probPosGivenPos[presentPos + self.delimit + prevPos]

    def getProbWGivenPosSimplified(self, word, pos):
        return self.probWordGivenPos[word + self.delimit + pos]

    def getAllProbWGivenPos(self, word):
        result = {entry: self.probWordGivenPos[entry] for entry in self.probWordGivenPos.keys() if entry.startswith(word)}
        if not result:
            # Word not seen in training data
            pos, prob = self.getPosForUnseenWord(word)
            result[word + self.delimit + pos] = prob
        return result

    # TODO - Change Logic
    def getProbWGivenPosHMM(self, word, pos):
        return self.probWordGivenPos[word + self.delimit + pos]
 
    def getProbPos(self, pos):
        return self.probPos[pos]

    def getAllPos(self):
        return self.probPos.keys()
    
    def getPosForUnseenWord(self, word):
        # print "Word Not Found: ", word
        predictedPos = 'noun'
        if self.containsDigit(word):
            predictedPos = 'num'
        else:
            suffixOfWord = self.checkSuffix(word)
            #print suffixOfWord
            if suffixOfWord != None:
                maxProb = 0 
                bestPos = ''
                for entry in self.suffixAndPos:
                    if entry.startswith(suffixOfWord):
                        #print "Checking: ", entry
                        #print "Starts! "
                        suffix, pos = entry.split(self.delimit)
                        currentValue = self.probSuffixPos[entry] * self.probPos[pos]
                        #print currentValue
                        if currentValue > maxProb:
                            maxProb = currentValue
                            bestPos = pos
                #probValues = [(self.probSuffixPos[entry] * self.probPos[entry.split(self.delimit)[1]], entry) for entry in self.suffixAndPos.keys() if entry.startswith(suffixOfWord)]
                predictedPos = bestPos 
                
        # Update Model 
        calculatedProb = self.updateModel(word, predictedPos)
        #print "Word Not Found: Predicted: ", predictedPos
        return predictedPos, calculatedProb

