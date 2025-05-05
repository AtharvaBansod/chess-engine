from flask import Flask, request,jsonify
from updateBoard import updateBoard
app = Flask(__name__)
chessBoard = [['__' for _ in range(8)] for _ in range(8)]
chessBoard[0][0] = chessBoard[0][7] = 'RB'  
chessBoard[0][1] = chessBoard[0][6] = 'NB'  
chessBoard[0][2] = chessBoard[0][5] = 'BB'  
chessBoard[0][3] = 'QB'  
chessBoard[0][4] = 'KB'  
chessBoard[1] = ['iB' for _ in range(8)]  
chessBoard[7][0] = chessBoard[7][7] = 'RW'  
chessBoard[7][1] = chessBoard[7][6] = 'NW'  
chessBoard[7][2] = chessBoard[7][5] = 'BW'  
chessBoard[7][3] = 'QW'  
chessBoard[7][4] = 'KW'  
chessBoard[6] = ['iW' for _ in range(8)]  

@app.route('/move', methods=['POST'])
def move():
    data = request.json
    move = data.get('move') 
    updateBoard(move, chessBoard)
    # minMax input (chessBoard)
    # minMax updates Board (chessBoard) 
    return jsonify({'message': 'Move processed successfully', 'updatedBoard': chessBoard}), 200

if __name__ == '__main__':
    app.run(debug=True, port=8081)