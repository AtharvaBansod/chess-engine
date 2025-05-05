
def isInBounds(r, c):
    return 0 <= r < 8 and 0 <= c < 8

def isSameColor(piece, target):
    return target != '__' and target[1] == piece[1]

def checkAvail(chessBoard,fromRow, fromCol, toRow, toCol):
    stepRow = (toRow - fromRow) // max(1, abs(toRow - fromRow))
    stepCol = (toCol - fromCol) // max(1, abs(toCol - fromCol))
    r, c = fromRow + stepRow, fromCol + stepCol
    while r != toRow or c != toCol:
        if chessBoard[r][c] != '__':
            return False
        r += stepRow
        c += stepCol
    return True

def notValid(move,chessBoard):
    fromPos, toPos = move.split()
    # fromRow, fromCol = int(fromPos[0]), int(fromPos[1])
    # toRow, toCol = int(toPos[0]), int(toPos[1])
    fromRow = int(fromPos[0])
    fromCol = int(fromPos[1])
    toRow = int(toPos[0])
    toCol = int(toPos[1])

    
    
    piece = chessBoard[fromRow][fromCol]
    target = chessBoard[toRow][toCol]

    if piece == '__':
        return True

    pieceType = piece[0]
    pieceColor = piece[1]

    if isSameColor(piece, target):
        print("Same color...")
        return True

    if pieceType == 'N':  # Knight
        validMoves = [(2, 1), (2, -1), (-2, 1), (-2, -1), (1, 2), (1, -2), (-1, 2), (-1, -2)]
        return (toRow - fromRow, toCol - fromCol) not in validMoves

    if pieceType == 'R':  # Rook
        if fromRow == toRow or fromCol == toCol:
            return not checkAvail(chessBoard,fromRow, fromCol, toRow, toCol)
        return True

    if pieceType == 'B':  # Bishop
        if abs(toRow - fromRow) == abs(toCol - fromCol):
            return not checkAvail(fromRow, fromCol, toRow, toCol)
        return True

    if pieceType == 'Q':  # Queen
        if fromRow == toRow or fromCol == toCol or abs(toRow - fromRow) == abs(toCol - fromCol):
            return not checkAvail(fromRow, fromCol, toRow, toCol)
        return True

    if pieceType == 'K':  # King
        validMoves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1)]
        return (toRow - fromRow, toCol - fromCol) not in validMoves

    if pieceType == 'i':  # Pawn
        direction = 1 if pieceColor=='W' else -1
        # print(fromRow,' ',fromCol,' ',toRow,' ',toCol,'\n')
        
        if fromCol == toCol and chessBoard[toRow][toCol] == '__':
            print("into ifffff")
            if fromRow - toRow == direction or (fromRow == (6 if pieceColor == 'W' else 1) and fromRow - toRow == 2*direction and chessBoard[fromRow - direction][fromCol] == '__'):
                print('reacchddddd')
                return False #means valid
        elif abs(fromCol - toCol) == 1 and toRow - fromRow == direction and chessBoard[toRow][toCol] != '__' and not isSameColor(piece, chessBoard[toRow][toCol]):
            return False
        print("herrrrrreee is the helllll...")
        return True #means not valid

    return False

def updateBoard(move,chessBoard):
    print('You played ', move)

    if notValid(move,chessBoard):
        print("Invalid move!")
        return

    fromPos, toPos = move.split()

    fromRow = int(fromPos[0])
    fromCol = int(fromPos[1])
    toRow = int(toPos[0])
    toCol = int(toPos[1])

    piece = chessBoard[fromRow][fromCol]
    chessBoard[fromRow][fromCol] = '__'
    chessBoard[toRow][toCol] = piece

    return chessBoard



