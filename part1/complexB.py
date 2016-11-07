import sys, math, copy
from operator import itemgetter

# Returns Product of prior and emission probs for all possible POS
def findInitialProbabilities(maxValues, allPos, posInd, probObj, word):
    start = '#SW#'
    initial = getAllPossiblePosForWord(word, allPos, probObj)
    
    for entry in initial:
        initial[entry] *= probObj.getProbNextPosGivenPrevPos(start, entry)
    #print "Initial: ", initial

    for entry in initial:
        maxValues[0][posInd[entry]] = (initial[entry], entry)
    #print maxValues[0]

# Returns a dict with pos as key and emission probability as value
def getAllPossiblePosForWord(word, allPos, probObj):
    allPossiblePos = {} # Pos: Emission Probability
    
    if not probObj.checkWordPresent(word):
        #print word, "Word not present"
        pos, prob = probObj.getPosForUnseenWord(word)
        #print pos, prob
        allPossiblePos[pos] = prob
    else:
        #print "Word Present"
        for pos in allPos:
            prob = probObj.getProbWGivenPosSimplified(word, pos)
            #print "word", word, "pos: ", pos, "Prob: ", prob
            if prob > 0:
                #print "pos: " ,pos
                allPossiblePos[pos] = prob
    #print allPossiblePos
    return allPossiblePos
        
# Making the dict posInd -> key = pos, value = index of maxValues matrix
def setPosIndexes(allPos, posInd):
    co = 0
    for pos in allPos:
        posInd[pos] = co
        co += 1
    #print posInd

def findKeyFromValue(d, ind):
    for key, val in d.iteritems():
        if val == ind:
            return key

def findPosForNextIteration(arr, ind, posInd):
    pos = []
    for i in range(len(arr[ind])):
        if arr[ind][i][0] > 0:
            pos.append((arr[ind][i][0], findKeyFromValue(posInd, i)))
    return pos
            
def findNonZeroValues(arr, i):
    return [i for i in arr[i] if i[0] > 0]

# Populating the matrix for max Probabilities across the sequence
def populateMatrix(arr, probObj, allPos, posInd, sentence):
    posForNextIteration = findNonZeroValues(arr, 0)
    complexHopPos = copy.deepcopy(posForNextIteration)
    ##print "POS fOR NEXT ITERATION: ", posForNextIteration
    count = 1
    for word in sentence[1:]:
        currentPos = getAllPossiblePosForWord(word, allPos, probObj)
        #print "All Possible Pso for current word: ", currentPos
        for pos in currentPos:
            tempValues = []
            #print "Word: POS: ", word, pos
            #print previousPos[0], probObj.getProbNextPosGivenPrevPos(previousPos[1], pos), currentPos[pos]
            #tempValues = [(previousPos[0] * probObj.getProbNextPosGivenPrevPos(previousPos[1], pos) * currentPos[pos], previousPos[1]) for previousPos in posForNextIteration]
            for previousPos in posForNextIteration:
                ##print "previousPos[0] : ", previousPos[0]
                #print "trans: ", probObj.getProbNextPosGivenPrevPos(previousPos[1], pos)
                #print "emission: ", currentPos[pos]
                tempValues.append(tuple((previousPos[0] * probObj.getProbNextPosGivenPrevPos(previousPos[1], pos) * currentPos[pos], previousPos[1])))
            # Check Si-2 for Si
            if count > 1:
                #tempValues += [(previousPos[0] * probObj.getProbNextPosGivenPrevPos(previousPos[1], pos) * currentPos[pos], previousPos[1]) for previousPos in complexHopPos]     
                #print "Complex: ", complexHopPos 
                for previousPos in complexHopPos:
                    #print "previousPos[0]: ", previousPos[0]
                    #print "trans: ", probObj.getProbNextPosGivenPrevPos(previousPos[1], pos)
                    #print "emission: ", currentPos[pos]
                    tempValues.append(tuple((previousPos[0] * probObj.getProbNextPosGivenPrevPos(previousPos[1], pos) * currentPos[pos], previousPos[1])))
                
                # Storing all pos of next to next hop to check later
                complexHopPos = zip(currentPos.values(), currentPos.keys())
                
            #print "TempValues: ", tempValues
            if tempValues:
                arr[count][posInd[pos]] = max(tempValues, key=itemgetter(0))
            else:
                for entry in arr[count - 1]:
                    if entry[1] != 0:
                        #tempValues.append((previousPos[1], 0.5))
                        possiblePos1 = (0.001, findKeyFromValue(posInd, arr[count-1].index(entry)))
                        break
                if count > 1:
                    for entry in arr[count - 2]:
                        if entry[1] != 0 :
                            #tempValues.append((previousPos[1], 0.5))
                            possiblePos2 = (0.001, findKeyFromValue(posInd, arr[count-2].index(entry)))
                            break
                if probObj.getProbPos(possiblePos1) > probObj.getProbPos(possiblePos2):
                    arr[count][posInd[pos]] = (0.001, possiblePos1)
                else:
                    arr[count][posInd[pos]] = (0.001, possiblePos2)
                    
                
            #print "ARR: ", arr[count]
        posForNextIteration = findPosForNextIteration(arr, count, posInd)
        #print "POS fOR NEXT ITERATION: ", posForNextIteration
        count += 1 
    #for i in range(len(arr)):
        #print arr[i]

# finds max value in list which has a pos
def maxLast(myList):
    value = max(myList, key=itemgetter(0))
    if value[1] == 0:
        for val in myList:
            if val[1] != 0:
                return myList.index(val)
    return myList.index(value)

def moveForward(arr, posInd, probObj, sentence):
    result = []
    marginalProbs = []
    for i in range(len(arr)):
        maxValInd = maxLast(arr[i])
        #print maxValInd
        result.append(arr[i][maxValInd][1])
        marginalProbs.append(arr[i][maxValInd][0])
    return result, marginalProbs

def forwardBackwardAlgo(arr, posInd, probObj, sentence):
    return moveForward(arr,posInd, probObj, sentence)
    #moveBackward(arr, posInd, probObj, sentence)
    
def findPosComplex(probObj, sentence):
    allPos = probObj.getAllPos()
    posInd = {}
    setPosIndexes(allPos, posInd)
    maxValues = [[(0, 0)] * len(allPos) for i in range(len(sentence))]
    findInitialProbabilities(maxValues, allPos, posInd, probObj, sentence[0])
    populateMatrix(maxValues, probObj, allPos, posInd, sentence)
    forwardVal = forwardBackwardAlgo(maxValues, posInd, probObj, sentence)
    probObj.storeMarginalComplex(forwardVal[1], forwardVal[0], sentence)
    return [[forwardVal[0]], [forwardVal[1]]]


