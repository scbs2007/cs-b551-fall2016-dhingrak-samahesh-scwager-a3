import sys
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
        pos, prob = probObj.getPosForUnseenWord(word)
        allPossiblePos[pos] = prob
    else:
        for pos in allPos:
            prob = probObj.getProbWGivenPosSimplified(word, pos)
            if prob > 0:
                allPossiblePos[pos] = prob
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
            #for key, val in posInd.iteritems():
            #    if val == i:
            #        pos.append((arr[ind][i][0], key))
            #        break
    return pos
            
def findNonZeroValues(arr, i):
    return [i for i in arr[i] if i[0] > 0]

# Populating the matrix for max Probabilities across the sequence
def populateMatrix(arr, probObj, allPos, posInd, sentence):
    #print sentence
    posForNextIteration = findNonZeroValues(arr, 0) #[i for i in arr[0] if i[0] > 0]
    #print "POS fOR NEXT ITERATION: ", posForNextIteration
    # Earlier both God and I knew what was happening in this function, now only he knows!
    count = 1
    for word in sentence[1:]:
        currentPos = getAllPossiblePosForWord(word, allPos, probObj)
        for pos in currentPos:
            tempValues = []
            #print "Word: POS: ", word, pos
            tempValues = [(previousPos[0] * probObj.getProbNextPosGivenPrevPos(previousPos[1], pos) * currentPos[pos], previousPos[1]) for previousPos in posForNextIteration]
            #for previousPos in posForNextIteration:
            #    tempValues.append(tuple((previousPos[0] * probObj.getProbNextPosGivenPrevPos(previousPos[1], pos) * currentPos[pos], previousPos[1])))
            #print "TempValues: ", tempValues
            
            arr[count][posInd[pos]] = max(tempValues, key=itemgetter(0))
            #print "ARR: ", arr[count]
        posForNextIteration = findPosForNextIteration(arr, count, posInd)
        #print "POS fOR NEXT ITERATION: ", posForNextIteration
        count += 1 
    #for i in range(len(arr)):
    #    print arr[i]

# Backtracking on the maxValues matrix to generate the POS sequence
def backTrack(arr, posInd):
    result = []
    l = len(arr)
    lastRow = arr[l - 1]
    maxLastRow = lastRow.index(max(lastRow, key=itemgetter(0)))
    result.append(findKeyFromValue(posInd, maxLastRow))
    for i in range(l - 1, 0, -1):
        cellValue = arr[i][maxLastRow][1]
        result.append(cellValue)
        maxLastRow = posInd[cellValue]
    result.reverse()
    #print result
    return result

def findPosHmm(probObj, sentence):
    allPos = probObj.getAllPos()
    posInd = {}
    setPosIndexes(allPos, posInd)
    maxValues = [[(0, 0)] * len(allPos) for i in range(len(sentence))]
    findInitialProbabilities(maxValues, allPos, posInd, probObj, sentence[0])
    populateMatrix(maxValues, probObj, allPos, posInd, sentence)
    return [[backTrack(maxValues, posInd)], []]
    #sys.exit(0)
