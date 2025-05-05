class GameState():
    def __init__(self):

        self.board = [
            ["RB", "NB", "BB", "QB", "KB", "BB", "NB", "RB"],
            ["iB", "iB", "iB", "iB", "iB", "iB", "iB", "iB"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["iW", "iW", "iW", "iW", "iW", "iW", "iW", "iW"],
            ["RW", "NW", "BW", "QW", "KW", "BW", "NW", "RW"]
        ]
        self.moveFunctions = {'i':self.getPawnMoves, 'R':self.getRookMoves, 'B':self.getBishopMoves, 'N': self.getKnightMoves, 'Q': self.getQueenMoves, 'K':self.getKingMoves}
        self.whiteToMove = True
        self.moveLog = []
        self.whiteKingLocation = (7,4)
        self.blackKingLocation = (0,4)
        self.checkmate = False
        self.stalemate = False
        self.isInCheck = False
        self.pins = []
        self.checks = [] 
        self.enpassantpossible=()
        self.currentCastlingRight = CastleRights(True, True, True, True)
        self.castleRightsLog = [CastleRights(self.currentCastlingRight.wks, self.currentCastlingRight.bks,self.currentCastlingRight.wqs, self.currentCastlingRight.bqs)]
    
    def makeMove(self,move): 
        self.board[move.startRow][move.starCol] = "--"
        self.board[move.endRow][move.endCol] = move.pieceMoved
        self.moveLog.append(move)
        self.whiteToMove = not self.whiteToMove

        # update Kings location
        if move.pieceMoved == "KW":
            self.whiteKingLocation = (move.endRow, move.endCol)
        elif move.pieceMoved == "KB":
            self.blackKingLocation = (move.endRow, move.endCol)

        # Pawn Promotionn !
        if move.isPawnPromotion:
            self.board[move.endRow][move.endCol] = move.pieceMoved[1] + "Q"

        # Enpassant Move
        if move.isEnpassant:
            self.board[move.startRow][move.endCol] = "--"
        # update enpassantPossible variable
        if move.pieceMoved[0] == "i" and abs(move.startRow - move.endRow) ==2:
            self.enpassantpossible = ((move.startRow + move.endRow)//2, move.startCol)
        else:
            self.enpassantpossible =()

        # Castle Move
        if move.isCastleMove:
            if move.endCol - move.startCol == 2:
                self.board[move.endRow][move.endCol-1] = self.board[move.endRow][move.endCol+1]
                self.board[move.endRow][move.endCol + 1] = "--"
            else: 
                self.board[move.endRow][move.endCol+1] = self.board[move.endRow][move.endCol-2]
                self.board[move.endRow][move.endCol-2] = "--"

        # Update Castling rights - rook nd king move
        self.updateCastleRights(move)
        self.castleRightsLog.append(CastleRights(self.currentCastlingRight.wks, self.currentCastlingRight.bks,self.currentCastlingRight.wqs, self.currentCastlingRight.bqs))


    def undoMove(self):
        if len(self.moveLog) !=0:
            move = self.moveLog.pop()
            self.board[move.startRow][move.startCol] = move.pieceMoved
            self.board[move.endRow][move.endCol] = move.pieceCaptured
            self.whiteToMove = not self.whiteToMove

            # undo Kings location
            if move.pieceMoved == "KW":
                self.whiteKingLocation = (move.startRow, move.startCol)
            elif move.pieceMoved == "KB":
                self.blackKingLocation = (move.startRow, move.startCol)

            # undo enPassant Move
            if move.isEnpassant:
                self.board[move.endRow][move.endCol] = "--"
                self.board[move.startRow][move.endCol] = move.pieceCaptured
                self.enpassantPossible = (move.endRow, move.endCol)
            if move.pieceMoved[0] == "i" and abs(move.startRow - move.endRow)==2:
                self.enpassantPossible = ()
            
            # Undo castling rights
            self.castleRightsLog.pop()
            self.currentCastlingRight = self.castleRightsLog[-1]

            # Undo castle move
            if move.isCastleMove:
                if move.endCol - move.startCol == 2:
                    self.board[move.endRow][move.endCol+1] = self.board[move.endRow][move.endCol-1]
                    self.board[move.endRow][move.endCol-1] = "--"
                else:
                    self.board[move.endRow][move.endCol-2] = self.board[move.endRow][move.endCol+1]
                    self.board[move.endRow][move.endCol+1] = "--"


    def updateCastleRights(self, move):
        if move.pieceMoved == "KW":
            self.currentCastlingRight.wks = False
            self.currentCastlingRight.wqs = False
        elif move.pieceMoved == "KB":
            self.currentCastlingRight.bks = False
            self.currentCastlingRight.bqs = False
        elif move.pieceMoved == "RW":
            if move.startRow ==7:
                if move.startCol == 0:
                    self.currentCastlingRight.wqs = False
                elif move.startCol == 7:
                    self.currentCastlingRight.wks = False 
        elif move.pieceMoved == "RB":
            if move.startRow == 0:
                if move.startCol == 0:
                    self.currentCastlingRight.bqs = False
                elif move.startCol == 7:
                    self.currentCastlingRight.bks = False 


    def checkForPinsAndChecks(self):
        pins = []
        checks = []
        isInCheck = False
        if self.whiteToMove:
            enemyColor = "B"
            allyColor = "W"
            startRow = self.whiteKingLocation[0]
            startCol = self.whiteKingLocation[1]
        else:
            enemyColor = "W"
            allyColor = "B"
            startRow = self.blackKingLocation[0]
            startCol = self.blackKingLocation[1]
        directions = ((-1,0),(0,-1),(1,0),(0,1),(-1,-1),(-1,1),(1,-1),(1,1))
        for j in range(len(directions)):
            d = directions[j]
            possiblePin = ()
            for i in range(1,8):
                endRow = startRow + d[0] * i
                endCol = startCol + d[1] * i
                if 0 <= endRow < 8 and 0 <= endCol < 8:
                    endPiece = self.board[endRow][endCol]
                    if endPiece[1] == allyColor and endPiece[0] != "K":
                        if possiblePin == ():
                            possiblePin = (endRow, endCol, d[0],d[1])
                        else:
                            break
                    elif endPiece[1] == enemyColor:
                        type = endPiece[0]
                        if(0 <= j <= 3 and type == "R") or \
                                (4<=j <=7 and type =="B") or \
                                (i==1 and type=="i" and ((enemyColor=="W" and 6<=j<=7) or (enemyColor =="B" and 4<=j<=5))) or \
                                (type =="Q") or (i == 1 and type == "k"):
                            if possiblePin == (): # no pieceeee blockingg, soo checkk
                                isInCheck = True
                                checks.append((endRow, endCol, d[0], d[1]))
                                break
                            else: # piece blocking so pin
                                pins.append(possiblePin)
                                break
                        else: # enemy piece not applying checks
                            break 
                else:
                    break # off-boarddd

        knightMoves = ((-2,-1), (-2,1), (-1,-2), (-1,1), (1,-2), (1,2), (2,-1), (2,1))
        for m in knightMoves:
            endRow = startRow + m[0]
            endCol = startCol + m[1]
            if 0 <= endRow < 8 and 0 <= endCol < 8:
                endPiece = self.board[endRow][endCol]
                if endPiece[1] == enemyColor and endPiece[0] == "N":
                    isInCheck = True
                    checks.append((endRow, endCol, m[0], m[1]))
        return isInCheck,pins,checks



    def getValidMoves(self):
        tempEnpassantPossible = self.enpassantpossible
        tempCastleRights = CastleRights(self.currentCastlingRight.wks,self.currentCastlingRight.bks,self.currentCastlingRight.wqs,self.currentCastlingRight.bqs)
        moves = []
        self.isInCheck, self.pins, self.checks = self.checkForPinsAndChecks()
        if self.whiteToMove:
            kingRow = self.whiteKingLocation[0]
            kingCol = self.whiteKingLocation[1]
        else:
            kingRow = self.blackKingLocation[0]
            kingCol = self.blackKingLocation[1]
        
        if self.isInCheck:
            if len(self.checks) == 1:
                moves = self.getAllPossibleMoves()
                # not sure
                check = self.checks[0]
                checkRow = check[0]
                checkCol = check[1]
                pieceChecking = self.board[checkRow][checkCol]
                validSquares = []
                if pieceChecking[0] == "N":
                    validSquares = [(checkRow, checkCol)]
                else:
                    for i in range(1,8):
                        validSquare = (kingRow + check [2] * i, kingCol + check[3]*i) # check[2] nd [3] are dirn of checkkks
                        validSquares.append(validSquare)
                        if validSquare[0] == checkRow and validSquare[1] == checkCol:
                            break
                for i in range(len(moves)-1,-1,-1):
                    if moves[i].pieceMoved[1] != "K":
                        if not (moves[i].endRow, moves[i].endCol) in validSquares:
                            moves.remove(moves[i])
            else: # double checks
                self.getKingMoves(kingRow,kingCol, moves)
              
        else: # no checkks so all possib movesss
            moves = self.getAllPossibleMoves()
            if self.whiteToMove:
                self.getCastleMoves(self.whiteKingLocation[0], self.whiteKingLocation[1],moves)
            else:
                self.getCastleMoves(self.blackKingLocation[0], self.blackKingLocation[1],moves)
                

        # old...
        # moves = self.getAllPossibleMoves() # generate all possible moves
        
        # for i in range (len(moves),-1,-1): 
        #     self.makeMove(moves[i]) # turn changes..but we dont hv to as its just check trials
        #     self.whiteToMove = not self.whiteToMove
        #     if self.inCheck():
        #         moves.remove(moves[i])
        #     self.whiteToMove = not self.whiteToMove # counter turns
        #     self.undoMove() # inBuild swith turns too..just bear w it ... balancing moves
        #     if len(moves) == 0:
        #         if self.inCheck():
        #             self.checkmate = True
        #         else: 
        #             self.stalemate = True
        #     else:
        #         self.checkmate = False
        #         self.stalemate = False
        self.enpassantpossible = tempEnpassantPossible
        self.currentCastlingRight = tempCastleRights
        return moves


    def inCheck(self):
        if self.whiteToMove:
            return self.squareUnderAttack(self.whiteKingLocation[0],self.whiteKingLocation[1])
        else:
            return self.squareUnderAttack(self.blackKingLocation[0],self.blackKingLocation[1])

    def squareUnderAttack(self,r,c):
        self.whiteToMove = not self.whiteToMove
        oppMoves = self.getAllPossibleMoves()
        self.whiteToMove = not self.whiteToMove
        for move in oppMoves:
            if move.endRow == r and move.endCol == c:
                return True
        return False

    def getAllPossibleMoves(self):
        moves = []
        for r in range(len(self.board)):
            for c in range(len(self.board[r])):
                turn = self.board[r][c][1]
                if (turn == 'W' and self.whiteToMove) or (turn == 'B' and not self.whiteToMove):
                    piece = self.board[r][c][0]
                    self.moveFunctions[piece](r,c,moves) # calls by appropriate mapping

                    # if piece == 'i':
                    #     self.getPawnMoves(r,c,moves)
                    # elif piece =="R":
                    #     self.getRookMoves(r,c,moves)
                    # .
                    # .
                    # so on...
                     
        return moves

    def getPawnMoves(self,r,c,moves):
        piecePinned = False
        pinDirection = ()
        for i in range(len(self.pins)-1,-1,-1):
            if self.pins[i][0] == r and self.pins[i][1] == c:
                piecePinned = True
                pinDirection = (self.pins[i][2],self.pins[i][3])
                self.pins.remove(self.pins[i])
                break

        if self.whiteToMove: # white Pawn Moves
            if self.board[r-1][c] == "--":
                if not piecePinned or pinDirection == (-1,0):
                    moves.append( Move((r,c), (r-1,c),self.board) )
                    if r == 6 and self.board[r-2][c] == "--":
                        moves.append( Move((r,c), (r-2,c),self.board) )
            # captures
            if c-1 >=0: 
                if self.board[r-1][c-1][1] == 'B': # enemy piece to capture
                    if not piecePinned or pinDirection == (-1,-1):
                        moves.append( Move((r,c), (r-1,c-1),self.board) )
                elif (r-1,c-1) == self.enpassantpossible:
                    if not piecePinned or pinDirection == (-1,-1):
                        moves.append( Move((r,c), (r-1,c-1),self.board),isEnpassantMove = True )
            if c+1 <= 7: 
                if self.board[r-1][c+1][1] == "B":
                    if not piecePinned or pinDirection == (-1,-1):
                        moves.append( Move((r,c), (r-1,c+1),self.board) )
                elif (r-1,c+1) == self.enpassantpossible:
                    if not piecePinned or pinDirection == (-1,-1):
                        moves.append( Move((r,c), (r-1,c+1),self.board),isEnpassantMove = True )
           
        
        else: # black Pawn Moves
            if self.board[r+1][c] == "--":
                if not piecePinned or pinDirection == (1,0):
                    moves.append( Move((r,c), (r+1,c),self.board) )
                    if r == 1 and self.board[r+2][c] == "--":
                        moves.append( Move((r,c), (r+2,c),self.board) )
            # captures
            if c-1 >=0:
                if self.board[r+1][c-1][1] == "W":
                    if not piecePinned or pinDirection == (1,-1):
                        moves.append( Move((r,c),(r+1,c-1),self.board) )
                elif (r+1,c-1) == self.enpassantpossible:
                    if not piecePinned or pinDirection == (-1,-1):
                        moves.append( Move((r,c), (r+1,c-1),self.board),isEnpassantMove = True )
           
            if c+1 <=7:
                if self.board[r+1][c+1][1] == "W":
                    if not piecePinned or pinDirection == (1,1):
                        moves.append( Move((r,c),(r+1,c+1),self.board) )
                elif (r+1,c+1) == self.enpassantpossible:
                    if not piecePinned or pinDirection == (-1,-1):
                        moves.append( Move((r,c), (r+1,c+1),self.board),isEnpassantMove = True )
           
        
    

    def getRookMoves(self,r,c,moves):
        piecePinned = False
        pinDirection = ()
        for i in range(len(self.pins)-1,-1,-1):
            if self.pins[i][0] == r and self.pins[i][1] == c:
                piecePinned = True
                pinDirection = (self.pins[i][2],self.pins[i][3])
                if self.board[r][c][1] !="Q":
                    self.pins.remove(self.pins[i])
                break

        directions = ( (-1,0),(0,-1),(1,0),(0,1) ) # up, left, down ,right
        enemyColor = "B" if self.whiteToMove else "W"

        for d in directions:
            for i in range(1,8):
                endRow = r + d[0] * i
                endCol = c + d[1] * i
                if 0 <= endRow < 8 and 0<= endCol < 8:
                    if not piecePinned or pinDirection == d or pinDirection == (-d[0],-d[1]):
                        endPiece = self.board[endRow][endCol]
                        if endPiece == "--":
                            moves.append( Move((r,c), (endRow,endCol), self.board) )
                        elif endPiece[0] == enemyColor:
                            moves.append( Move((r,c), (endRow,endCol), self.board) )
                            break
                        else: # friendly
                            break
                else: # off-board
                    break


    def getBishopMoves(self,r,c,moves):
        piecePinned = False
        pinDirection = ()
        for i in range(len(self.pins)-1,-1,-1):
            if self.pins[i][0] == r and self.pins[i][1] == c:
                piecePinned = True
                pinDirection = (self.pins[i][2],self.pins[i][3])
                self.pins.remove(self.pins[i])
                break

        directions = ((-1,-1), (-1,1), (1,-1),(1,1))
        enemyColor = "B" if self.whiteToMove else "W"

        for d in directions:
            for i in range(1,8):
                endRow = r + d[0] * i
                endCol = c + d[1] * i
                if 0 <= endRow < 8 and 0<= endCol < 8:
                    if not piecePinned or pinDirection == d or pinDirection == (-d[0], -d[1]):
                        endPiece = self.board[endRow][endCol]
                        if endPiece == "--":
                            moves.append( Move((r,c), (endRow,endCol), self.board) )
                        elif endPiece[0] == enemyColor:
                            moves.append( Move((r,c), (endRow,endCol), self.board) )
                            break
                        else: # friendlyyy
                            break
                else: # Offf-board
                    break


    def getKnightMoves(self,r,c,moves):
        piecePinned = False
        for i in range(len(self.pins)-1,-1,-1):
            if self.pins[i][0] == r and self.pins[i][1] ==c:
                piecePinned = True
                self.pins.remove(self.pins[i])
                break

        knightMoves = ((-2,-1), (-2,1), (-1,-2), (-1,1), (1,-2), (1,2), (2,-1), (2,1))
        allyColor = "W" if self.whiteToMove else "B"
        for m in knightMoves:
            endRow = r + m[0]
            endCol = c + m[1]
            if 0<= endRow < 8 and 0<=endCol<8:
                if not piecePinned:
                    endPiece = self.board[endRow][endCol]
                    if endPiece[0] != allyColor:
                        moves.append(Move((r,c),(endRow,endCol),self.board))


    def getQueenMoves(self,r,c,moves):
        self.getBishopMoves(r,c,moves)
        self.getRookMoves(r,c,moves)

    def getKingMoves(self,r,c,moves):
        rowMoves = (-1,-1,-1,0,0,1,1,1)
        colMoves = (-1,0,1,-1,1,-1,0,1)

        allyColor = "W" if self.whiteToMove else "B"
        for i in range(8):
            endRow = r + rowMoves[i]
            endCol = c + colMoves[i]
            if 0<= endRow < 8 and 0<=endCol<8:
                endPiece = self.board[endRow][endCol]
                if endPiece[0] != allyColor:
                    if allyColor == "W":
                        self.whiteKingLocation = (endRow,endCol)
                    else:
                        self.blackKingLocation = (endRow,endCol)
                    isInCheck, pins, checks = self.checkForPinsAndChecks()
                    if not isInCheck:
                        moves.append(Move((r,c),(endRow,endCol),self.board))
                    if allyColor == "W":
                        self.whiteKingLocation = (r,c)
                    else:
                        self.blackKingLocation = (r,c)
        self.getCastleMoves(r,c,moves)
    
    def getCastleMoves(self,r,c,moves):
        if self.squareUnderAttack(r,c):
            return
        if (self.whiteToMove and self.currentCastlingRight.wks) or (not self.whiteToMove and self.currentCastlingRight.bks):
            self.getKingsideCastleMoves(r,c,moves)
        if (self.whiteToMove and self.currentCastlingRight.wqs) or (not self.whiteToMove and self.currentCastlingRight.wqs):
            self.getQueensideCastleMoves(r,c,moves)

    def getKingsideCastleMoves(self,r,c,moves):
        if self.board[r][c+1] == "--" and self.board[r][c+2] == "--":
            if not self.squareUnderAttack(r, c+1) and not self.squareUnderAttack(r,c+2):
                moves.append(Move((r,c),(r,c+2),self.board, isCastleMove=True))
    
    def getQueensideCastleMoves(self,r,c,moves):
        if self.board[r][c-1] == "--" and self.board[r][c-2] == "--":
            if not self.squareUnderAttack(r, c-1) and not self.squareUnderAttack(r,c-2):
                moves.append(Move((r,c),(r,c-2),self.board, isCastleMove=True))


class CastleRights():
    def __init__(self, wks, bks,wqs, bqs):
        self.wks = wks
        self.bks = bks
        self.wqs = wqs
        self.bqs = bqs




class Move():

    ranksToRows = {"1": 7,"2": 6,"3": 5,"4": 4,"5": 3,"6": 2,"7": 1,"8": 0}
    rowsToRanks = {v:k for k,v in ranksToRows.items()}
    filesToCols = {"a": 0, "b": 1, "c": 2, "d": 3, "e": 4, "f": 5, "g": 6, "h": 7}
    colsToFiles = {v:k for k,v in filesToCols.items()}

    def __init__(self, startSq, endSq, board, isEnpassantMove = False, isCastleMove=False):
        self.startRow, self.startCol = startSq[0], startSq[1]
        self.endRow, self.endCol = endSq[0], endSq[1]
        self.pieceMoved = board[self.startRow][self.startCol]
        self.pieceCaptured = board[self.endRow][self.endCol]
        # pawn Promotion
        self.isPawnPromotion = (self.pieceMoved == "iW" and self.endRow == 0) or (self.pieceMoved == "iB" and self.endRow == 7)
        # EnPassant
        self.isEnpassantMove = isEnpassantMove
        if self.isEnpassantMove:
            self.pieceCaptured = "iW" if self.pieceMoved == "iB" else "iB"
            
        # Castle Move
        self.isCastleMove = isCastleMove

        self.moveID = self.startRow * 1000 + self.startCol * 100 + self.endRow * 10 + self.endCol

    def __eq__(self,other): 
        if isinstance(other,Move):
            return self.moveID == other.moveID
        return False

    def getChessNotation(self):
        return self.getRankFile(self.startRow, self.startCol) + self.getRankFile(self.endRow,self.endCol)

    def getRankFile(self,r,c):
        return self.colsToFiles[c] + self.rowsToRanks[r]
        


