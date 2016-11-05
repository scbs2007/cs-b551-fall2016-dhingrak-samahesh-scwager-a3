# For Simplified Bayes Net
#
def findPosSimplified(probObj, sentence):
    #print "In simplified"
    predictedPos = []
    probValues = []
    for eachWord in sentence:
        highestProb = 0
        bestPos = ""
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
        if highestProb == 0:
            bestPos = probObj.getBestEstimatedPos(eachWord)

        predictedPos.append(bestPos)
        probValues.append(round(highestProb, 2))
    #print predictedPos
    #print probValues
    return [[predictedPos], [probValues]]
