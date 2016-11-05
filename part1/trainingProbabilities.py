from __future__ import division
from collections import Counter
#import cProfile, pstats, StringIO

class TrainingProbs:
    
    def __init__(self):
        # POS based on common suffixes - For Predicting POS of words not present in Training data
        # http://southcentral.edu/images/departments/ASC/documents/Suffixes_that_Indicate_Part_of_Speech_2.pdf
        '''self.suffixPos = {  'sion': ['noun'], 'tion': ['noun'], 'ance': ['noun'], 'ence': ['noun'], 'hood': ['noun'], 'ment': ['noun'], 'ness': ['noun'], \
                            'like': ['adj'], 'able': ['adj'], 'ible': ['adj'], \
                            'ion': ['noun'], 'acy': ['noun'], 'age': ['noun'], 'ism': ['noun'], 'ist': ['noun'], 'ity': ['noun'], \
                            'ful': ['adj'], 'ish': ['adj'], 'ous': ['adj'], 'ate': ['adj'], \
                            'ify': ['verb'], 'ate': ['verb'], 'ize': ['verb'], \
                            'ar': ['noun'], 'or': ['noun'], \
                            'ic': ['adj'], 'al': ['adj'], \
                            'ly': ['adv', 'adj'], \
                            'en': ['verb'], \
                            'y': ['noun', 'adj'] \
                        }
         self.suffixPos = {  
                            'sion': [{'noun': }], 'tion': [{'noun': }], 'ance': [{'noun': }], 'ence': [{'noun': }], \
                            'hood': [{'noun': }], 'ment': [{'noun': }], 'ness': [{'noun': }], \
                            'like': [{'adj': }], 'able': [{'adj': }], 'ible': [{'adj': }], \
                            'ion': [{'noun': }], 'acy': [{'noun': }], 'age': [{'noun': }], 'ism': [{'noun': }], 'ist': [{'noun': }], 'ity': [{'noun': }], \
                            'ful': [{'adj': }], 'ish': [{'adj': }], 'ous': [{'adj': }], 'ate': [{'adj': }], \
                            'ify': [{'verb': }], 'ate': [{'verb': }], 'ize': [{'verb': }], \
                            'ar': [{'noun': }], 'or': [{'noun': }], \
                            'ic': [{'adj': }], 'al': [{'adj': }], \
                            'ly': [{'adv': , 'adj':}], \
                            'en': [{'verb': }], \
                            'y': [{'noun': , 'adj': }] \
                         }'''
        # Most Common Suffixes
        self.suffix = ['sion', 'tion', 'ance', 'ence', 'hood', 'ment', 'ness', 'like', 'able', 'ible', \
                        'ion', 'acy', 'age', 'ism', 'ist', 'ity', 'ful', 'ish', 'ous', 'ate', 'ify', 'ize', 'ing',\
                        'ar', 'or', 'ic', 'al', 'ly', 'en', 'ed', 'y']
        
        # Most Common Suffixes with their POSs
        self.suffixAndPos = ['sion|noun', 'tion|noun', 'ance|noun', 'ence|noun', 'hood|noun', 'ment|noun', 'ness|noun', 'like|adj', 'able|adj', 'ible|adj', \
        'ion|noun', 'acy|noun', 'age|noun', 'ism|noun', 'ist|noun', 'ity|noun', 'ful|adj', 'ish|adj', 'ous|adj', 'ate|adj', 'ify|verb', 'ing|verb', 'ate|verb', 'ize|verb', \
        'ar|noun', 'or|noun', 'ic|adj', 'al|adj', 'ly|adv', 'ly|adj', 'en|verb', 'ed|verb', 'y|noun', 'y|adj']
        
        self.probSuffixPos = Counter() # Probability of word with suffix being a pos. eg: P of word with suffix 'sion' being a 'noun'
        self.probPos = Counter() # P(S)
        self.probPosGivenPos = Counter() # P(Si+1|Si)
        self.probWordGivenPos = Counter() # P(W|S)
        self.countOfPos = 0 # total number of Pos in training data
        self.delimit = '|'
        self.numberOfSentences = 0
        self.startOfSentence = '#SW#'

    # Check if a word has a suffix that we need
    def checkSuffix(self, word):
        for entry in self.suffix:
            if word.endswith(entry):
                return entry
        return None

    # Check if a word has a suffix and a pos that we need
    def checkPos(self, suffix, pos):
        suffixPos = suffix + '|' + pos
        if suffixPos in self.suffixAndPos:
            return suffixPos
        return None

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

                # Adding Counts of all POSpeeches
                self.probPos[pos] += 1
                
                # Adding Counts of all <word>|<pos>
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

    # Check if word contains digit
    def containsDigit(self, word):
        for ch in word:
            if ch.isdigit():
                return True
        return False
    
    # Calculate P(S)
    def calculatePosProb(self):
        for entry in self.probPos.keys():
            self.probPos[entry] /= self.countOfPos
            print "POS: entry: ", entry, self.probPos[entry]

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

    # Getters
    def getProbWGivenPosSimplified(self, word, pos):
        return self.probWordGivenPos[word + self.delimit + pos]
    
    def getProbPos(self, pos):
        return self.probPos[pos]

    def getAllPos(self):
        return self.probPos.keys()
    
    def getBestEstimatedPos(self, word):
        print "Word Not Found: ", word
        predictedPos = 'noun'
        if self.containsDigit(word):
            predictedPos = 'num'
        elif word.endswith("'s"):
            predictedPos = 'noun'
        elif len(word) > 2:
            suffixOfWord = self.checkSuffix(word)
            #print suffixOfWord
            if suffixOfWord != None:
                maxProb = 0 
                bestPos = ''
                for entry in self.suffixAndPos:
                    if entry.startswith(suffixOfWord):
                        print "Checking: ", entry
                        print "Starts! "
                        suffix, pos = entry.split(self.delimit)
                        currentValue = self.probSuffixPos[entry] * self.probPos[pos]
                        print currentValue
                        if currentValue > maxProb:
                            maxProb = currentValue
                            bestPos = pos
                #probValues = [(self.probSuffixPos[entry] * self.probPos[entry.split(self.delimit)[1]], entry) for entry in self.suffixAndPos.keys() if entry.startswith(suffixOfWord)]
                predictedPos = bestPos 
        print "Word Not Found: Predicted: ", predictedPos
        return predictedPos

