import random


pieceScore = {"K":0, "Q":9,"R":5,"B":3,"N":3,"p":1}
CHECKMATE=1000
STALEMATE=0
DEPTH = 3



def scoreMaterial(board):
    score = 0
    for row in board:
        for square in row:
            if square[1] == "W":
                score += pieceScore[square[0]]
            elif square[1] == "B":
                score -= pieceScore[square[0]]
    return score


# gs and valid moves are missing..learn it..... depth of 2 
def findBestMoveGreedy(gs, validMoves):
    turnMultiplier = 1 if gs.whiteToMove else -1
    opponentsMinMaxScore = CHECKMATE     
    bestPlayerMove = None
    random.shuffle(validMoves)
    for playerMove in validMoves:
        gs.makeMove(playerMove)
        opponentsMoves = gs.getValidMoves()
        if gs.stalemate:
            opponentsmaxScore = STALEMATE
        elif gs.checkmate:
            opponentsmaxScore = -CHECKMATE
        else:
            for opponentmove in opponentsMoves:
                gs.makeMove(opponentmove)
                gs.getValidMoves() #..generates valid move ..helpful for further decissions
                if gs.checkmate:
                    score = CHECKMATE
                elif gs.stalemate:
                    score = STALEMATE
                else:
                    score = -turnMultiplier * scoreMaterial(gs.board)
                if score > opponentsmaxScore:
                    opponentsmaxScore = score
                gs.undoMove()
        
        if opponentsmaxScore < opponentsMinMaxScore :
            opponentsMinMaxScore = opponentsmaxScore
            bestPlayerMove = playerMove
        gs.undoMove()
    
    return bestPlayerMove


# helper for min-max & NegaMax method to make first recursive call
def findBestMove(gs, validMoves):
    global nextMove, counter
    nextMove = None
    #findMoveMinMax(gs,validMoves,DEPTH,gs.whiteToMove)   # for miniMax
    # findMoveNegaMax(gs,validMoves,DEPTH, 1 if gs.whiteToMove else -1)   # for NegaMax
    counter = 0
    findMoveNegaMaxAlphaBeta(gs,validMoves,DEPTH, -CHECKMATE,CHECKMATE,1 if gs.white_to_move else -1)   # for NegaMaxAlphaBeta
    print(counter)
    return nextMove


def findMoveMinMax(gs, validMoves, depth, whiteToMove:bool):
    global nextMove,counter
    counter+=1
    if depth == 0:
        return scoreMaterial(gs.board)

    if whiteToMove:
        maxScore = - CHECKMATE
        for move in validMoves:
            gs.makeMove(move)
            nextMoves = gs.getValidMoves()
            score = findMoveMinMax(gs, nextMoves, depth-1, False) #..False coz we know its white-to-move
            if score > maxScore:
                maxScore = score
                if depth == DEPTH:
                    nextMove = move
            gs.undoMove()
        return maxScore
    else:
        minScore = CHECKMATE
        for move in validMoves:
            gs.makeMove(move)
            nextMoves = gs.getValidMoves()
            score = findMoveMinMax(gs, nextMoves, depth-1, True) #..True
            if score < minScore:
                minScore = score
                if depth == DEPTH:
                    nextMove = move
            gs.undoMove()
        return minScore


def findMoveNegaMax(gs, validMoves, depth, trunMultiplier):
    global nextMove,counter
    counter+=1
    if depth == 0:
        return trunMultiplier * scoreBoard(gs)
    
    maxScore = -CHECKMATE

    for move in validMoves:
        gs.makeMove(move)
        nextMoves = gs.getValidMoves()
        score = - findMoveNegaMax(gs, nextMoves, depth-1, -trunMultiplier)
        if score > maxScore:
            maxScore = score
            if depth == DEPTH:
                nextMove = move
        gs.undoMove()
    
    return maxScore 


def findMoveNegaMaxAlphaBeta(gs, validMoves, depth, alpha, beta, trunMultiplier):
    global nextMove, counter
    counter+=1
    if depth == 0:
        return trunMultiplier * scoreBoard(gs)
    
    maxScore = -CHECKMATE

    for move in validMoves:
        gs.makeMove(move)
        nextMoves = gs.getValidMoves()
        score = - findMoveNegaMaxAlphaBeta(gs, nextMoves, depth-1, -beta, -alpha, -trunMultiplier)
        if score > maxScore:
            maxScore = score
            if depth == DEPTH:
                nextMove = move
        gs.undoMove()
    
        if maxScore > alpha:   # Pruning happens
            alpha = maxScore
        if alpha>=beta:
            break

    return maxScore 


# Positive score is good for white
def scoreBoard(gs):
    if gs.checkmate:
        if gs.whiteToMove:
            return -CHECKMATE # black wins
        else: 
            return CHECKMATE # white wins
    elif gs.stalemate:
        return STALEMATE

    score = 0
    for row in gs.board:
        for square in row:
            if square[0] == "w":
                score += pieceScore[square[1]]
            elif square[0] == "b":
                score -= pieceScore[square[1]]
    return score   
