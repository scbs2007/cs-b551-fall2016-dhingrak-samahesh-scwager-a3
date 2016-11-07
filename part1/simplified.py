# For Simplified Bayes Net
#
import math
'''
def replaceGreater(p1, p2, best, pos):
    if p1 > p2:
        p2 = p1
'''

def findPosSimplified(probObj, sentence):
    #print "In simplified"
    predictedPos = []
    probValues = []
    for eachWord in sentence:
        bestPos = ""
        highestProb = 0
        for pos in probObj.getAllPos():
            # P(S|W) = P(W|S) * P(S)
            # Ignoring Denominator - constant
            probWgivenS = probObj.getProbWGivenPosSimplified(eachWord, pos) \
                          * probObj.getProbPos(pos)
            
            # Find POS with highest probability
            if probWgivenS > highestProb:
                highestProb = probWgivenS
                bestPos = pos
            
        # If word wasn't found in the training data
        if not highestProb:
            bestPos, highestProb = probObj.getPosForUnseenWord(eachWord)
            #print bestPos, highestPos

        predictedPos.append(bestPos)
        probValues.append(highestProb)
    #print predictedPos
    #print probValues
    return [[predictedPos], [probValues]]
