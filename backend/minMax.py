import random
import time


pieceScore = {"K": 0, "Q": 900, "R": 500, "B": 330, "N": 320, "p": 100}
CHECKMATE = 100000
STALEMATE = 0
DEPTH = 3
MAX_DEPTH = 6
SEARCH_TIME = 1.0
HINT_TIME = 0.5
INFINITY = CHECKMATE * 10

PAWN_TABLE = [
    [0, 0, 0, 0, 0, 0, 0, 0],
    [50, 50, 50, 50, 50, 50, 50, 50],
    [10, 10, 20, 30, 30, 20, 10, 10],
    [5, 5, 10, 25, 25, 10, 5, 5],
    [0, 0, 0, 20, 20, 0, 0, 0],
    [5, -5, -10, 0, 0, -10, -5, 5],
    [5, 10, 10, -20, -20, 10, 10, 5],
    [0, 0, 0, 0, 0, 0, 0, 0],
]

KNIGHT_TABLE = [
    [-50, -40, -30, -30, -30, -30, -40, -50],
    [-40, -20, 0, 0, 0, 0, -20, -40],
    [-30, 0, 10, 15, 15, 10, 0, -30],
    [-30, 5, 15, 20, 20, 15, 5, -30],
    [-30, 0, 15, 20, 20, 15, 0, -30],
    [-30, 5, 10, 15, 15, 10, 5, -30],
    [-40, -20, 0, 5, 5, 0, -20, -40],
    [-50, -40, -30, -30, -30, -30, -40, -50],
]

BISHOP_TABLE = [
    [-20, -10, -10, -10, -10, -10, -10, -20],
    [-10, 0, 0, 0, 0, 0, 0, -10],
    [-10, 0, 5, 10, 10, 5, 0, -10],
    [-10, 5, 5, 10, 10, 5, 5, -10],
    [-10, 0, 10, 10, 10, 10, 0, -10],
    [-10, 10, 10, 10, 10, 10, 10, -10],
    [-10, 5, 0, 0, 0, 0, 5, -10],
    [-20, -10, -10, -10, -10, -10, -10, -20],
]

ROOK_TABLE = [
    [0, 0, 0, 0, 0, 0, 0, 0],
    [5, 10, 10, 10, 10, 10, 10, 5],
    [-5, 0, 0, 0, 0, 0, 0, -5],
    [-5, 0, 0, 0, 0, 0, 0, -5],
    [-5, 0, 0, 0, 0, 0, 0, -5],
    [-5, 0, 0, 0, 0, 0, 0, -5],
    [-5, 0, 0, 0, 0, 0, 0, -5],
    [0, 0, 0, 5, 5, 0, 0, 0],
]

QUEEN_TABLE = [
    [-20, -10, -10, -5, -5, -10, -10, -20],
    [-10, 0, 0, 0, 0, 0, 0, -10],
    [-10, 0, 5, 5, 5, 5, 0, -10],
    [-5, 0, 5, 5, 5, 5, 0, -5],
    [0, 0, 5, 5, 5, 5, 0, -5],
    [-10, 5, 5, 5, 5, 5, 0, -10],
    [-10, 0, 5, 0, 0, 0, 0, -10],
    [-20, -10, -10, -5, -5, -10, -10, -20],
]

KING_TABLE = [
    [-30, -40, -40, -50, -50, -40, -40, -30],
    [-30, -40, -40, -50, -50, -40, -40, -30],
    [-30, -40, -40, -50, -50, -40, -40, -30],
    [-30, -40, -40, -50, -50, -40, -40, -30],
    [-20, -30, -30, -40, -40, -30, -30, -20],
    [-10, -20, -20, -20, -20, -20, -20, -10],
    [20, 20, 0, 0, 0, 0, 20, 20],
    [20, 30, 10, 0, 0, 10, 30, 20],
]

PIECE_TABLES = {"p": PAWN_TABLE, "N": KNIGHT_TABLE, "B": BISHOP_TABLE,
                "R": ROOK_TABLE, "Q": QUEEN_TABLE, "K": KING_TABLE}


class SearchCancelled(Exception):
    pass


def scoreMaterial(board):
    score = 0
    for row in board:
        for square in row:
            if square[0] == "w":
                score += pieceScore[square[1]]
            elif square[0] == "b":
                score -= pieceScore[square[1]]
    return score


def scoreBoard(gs):
    score = 0
    for r, row in enumerate(gs.board):
        for c, square in enumerate(row):
            if square == "--":
                continue
            piece = square[1]
            if square[0] == "w":
                score += pieceScore[piece] + PIECE_TABLES[piece][r][c]
            else:
                score -= pieceScore[piece] + PIECE_TABLES[piece][7 - r][c]
    return score


def moveOrderKey(move):
    score = 0
    if move.piece_captured != "--":
        score += 10 * pieceScore[move.piece_captured[1]] - pieceScore[move.piece_moved[1]] + 10000
    if move.is_pawn_promotion:
        score += 9000
    if move.is_castle_move:
        score += 50
    return -score


def orderMoves(moves):
    return sorted(moves, key=moveOrderKey)


def searchRoot(gs, rootMoves, depth, should_stop=None):
    turn = 1 if gs.white_to_move else -1
    best_move, best_score = None, -INFINITY
    alpha, beta = -INFINITY, INFINITY
    for move in rootMoves:
        gs.makeMove(move)
        try:
            score = -negaMaxAlphaBeta(gs, depth - 1, -beta, -alpha, -turn, should_stop)
        finally:
            gs.undoMove()
        if score > best_score:
            best_score, best_move = score, move
        alpha = max(alpha, score)
    return best_move, best_score


def findBestMove(gs, validMoves, depth=DEPTH, should_stop=None, time_limit=None, max_depth=MAX_DEPTH):
    rootMoves = orderMoves(validMoves)
    if not rootMoves:
        return None
    if time_limit is None:
        return searchRoot(gs, rootMoves, depth, should_stop)[0]

    deadline = time.monotonic() + time_limit
    best_move = rootMoves[0]
    for current_depth in range(1, max_depth + 1):
        def stop():
            if should_stop is not None and should_stop():
                return True
            return current_depth > depth and time.monotonic() > deadline
        try:
            move, score = searchRoot(gs, rootMoves, current_depth, stop)
        except SearchCancelled:
            if should_stop is not None and should_stop():
                raise
            break
        best_move = move
        rootMoves.remove(move)
        rootMoves.insert(0, move)
        if abs(score) >= CHECKMATE or time.monotonic() > deadline:
            break
    return best_move


def negaMaxAlphaBeta(gs, depth, alpha, beta, turn, should_stop=None):
    if should_stop is not None and should_stop():
        raise SearchCancelled()
    if depth == 0:
        return turn * scoreBoard(gs)

    moves = gs.getValidMoves()
    if not moves:
        return -(CHECKMATE + depth) if gs.checkmate else STALEMATE

    best = -INFINITY
    for move in orderMoves(moves):
        gs.makeMove(move)
        try:
            score = -negaMaxAlphaBeta(gs, depth - 1, -beta, -alpha, -turn, should_stop)
        finally:
            gs.undoMove()
        if score > best:
            best = score
        if best > alpha:
            alpha = best
        if alpha >= beta:
            break
    return best


def findBestMoveGreedy(gs, validMoves):
    turnMultiplier = 1 if gs.white_to_move else -1
    opponentsMinMaxScore = CHECKMATE
    bestPlayerMove = None
    random.shuffle(validMoves)
    for playerMove in validMoves:
        gs.makeMove(playerMove)
        opponentsMoves = gs.getValidMoves()
        if gs.stalemate:
            opponentsMaxScore = STALEMATE
        elif gs.checkmate:
            opponentsMaxScore = -CHECKMATE
        else:
            opponentsMaxScore = -CHECKMATE
            for opponentMove in opponentsMoves:
                gs.makeMove(opponentMove)
                gs.getValidMoves()
                if gs.checkmate:
                    score = CHECKMATE
                elif gs.stalemate:
                    score = STALEMATE
                else:
                    score = -turnMultiplier * scoreMaterial(gs.board)
                opponentsMaxScore = max(opponentsMaxScore, score)
                gs.undoMove()
        if opponentsMaxScore < opponentsMinMaxScore:
            opponentsMinMaxScore = opponentsMaxScore
            bestPlayerMove = playerMove
        gs.undoMove()
    return bestPlayerMove


def findMoveMinMax(gs, validMoves, depth, whiteToMove):
    if depth == 0:
        return scoreMaterial(gs.board), None
    best_move = None
    best_score = -INFINITY if whiteToMove else INFINITY
    for move in validMoves:
        gs.makeMove(move)
        score, _ = findMoveMinMax(gs, gs.getValidMoves(), depth - 1, not whiteToMove)
        gs.undoMove()
        if (whiteToMove and score > best_score) or (not whiteToMove and score < best_score):
            best_score, best_move = score, move
    return best_score, best_move


def findMoveNegaMax(gs, validMoves, depth, turnMultiplier):
    if depth == 0:
        return turnMultiplier * scoreBoard(gs), None
    best_move, best_score = None, -INFINITY
    for move in validMoves:
        gs.makeMove(move)
        score, _ = findMoveNegaMax(gs, gs.getValidMoves(), depth - 1, -turnMultiplier)
        gs.undoMove()
        if -score > best_score:
            best_score, best_move = -score, move
    return best_score, best_move
