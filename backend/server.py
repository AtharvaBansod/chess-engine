# from flask import Flask, request
# from flask_socketio import SocketIO, emit
# from ChessEngine2 import GameState  
# from minMax import findBestMove  
# from ChessEngine2 import Move 
# from flask_cors import CORS

# app = Flask(__name__)
# CORS(app)
# socketio = SocketIO(app, cors_allowed_origins="*")

# game_instances = {}

# @app.route('/')
# def home():
#     return "Chess Server !"

# @socketio.on('connect')
# def handle_connect():
#     print(f"User connected: {request.sid}")


# @socketio.on('join_game')
# def handle_join_game():
#     user_id = request.sid
#     gs = GameState()  
#     game_instances[user_id] = gs
    
#     valid_moves = [{'start_sq': [move.start_row, move.start_col], 'end_sq': [move.end_row, move.end_col]} for move in gs.getValidMoves()]
#     emit('valid_moves', {'valid_moves': valid_moves, 'board': gs.board}, room=user_id)
#     emit('game_started', {'message': 'Game against AI has started!'}, room=user_id)
#     print(valid_moves)

# @socketio.on('make_move')
# def handle_make_move(data):
#     user_id = request.sid
#     player_move_data = data.get('move')  
#     gs = game_instances.get(user_id)  

#     if gs:
#         player_move = Move(player_move_data['start_sq'], player_move_data['end_sq'], gs.board)
        
#         if player_move in gs.getValidMoves():
#             gs.makeMove(player_move)
            
#             emit('move_made', {'move': player_move.getChessNotation(), 'board': gs.board}, room=user_id)
            
            
#             ai_move = findBestMove(gs, gs.getValidMoves())
#             gs.makeMove(ai_move)
            
            
#             emit('move_made', {'move': ai_move.getChessNotation(), 'board': gs.board}, room=user_id)

            
#             valid_moves = [{'start_sq': [move.start_row, move.start_col], 'end_sq': [move.end_row, move.end_col]} for move in gs.getValidMoves()]

            
#             emit('valid_moves', {'valid_moves': valid_moves, 'board': gs.board}, room=user_id)
#         else:
#             emit('invalid_move', {'message': 'Invalid move! Try again.'}, room=user_id)
#     print("Move made by user")


# @socketio.on('disconnect')
# def handle_disconnect():
#     user_id = request.sid
#     if user_id in game_instances:
#         del game_instances[user_id] 
#     print(f"User disconnected: {user_id}")


# if __name__ == '__main__':
#     socketio.run(app,debug=True,port=5000)
#     print("Server Running...")



from flask import Flask, request
from flask_socketio import SocketIO, emit, join_room, leave_room
from ChessEngine2 import GameState  # Your custom GameState class
from minMax import findBestMove  # AI logic for best move
from ChessEngine2 import Move  # Assuming Move class is in move.py
from flask_cors import CORS
import uuid

# Initialize Flask app and SocketIO
app = Flask(__name__)
CORS(app)
socketio = SocketIO(app, cors_allowed_origins="*", manage_session=False)

# Global variables to store game instances and multiplayer data
game_instances = {}        # For AI games: {user_id: GameState}
multiplayer_games = {}     # For Multiplayer: {game_id: {'players': [player1_id, player2_id], 'game_state': GameState, 'turn': 'white'}}
waiting_players = []       # Queue for multiplayer matchmaking

@app.route('/')
def home():
    return "Chess Server!"

@socketio.on('connect')
def handle_connect():
    print(f"User connected: {request.sid}")

@socketio.on('join_game')
def handle_join_game():
    user_id = request.sid
    gs = GameState()
    game_instances[user_id] = gs

    # Emit initial valid moves and the board state to the player
    valid_moves = [
        {'start_sq': [move.start_row, move.start_col], 'end_sq': [move.end_row, move.end_col]}
        for move in gs.getValidMoves()
    ]
    emit('valid_moves', {'valid_moves': valid_moves, 'board': gs.board}, room=user_id)
    emit('game_started', {'message': 'Game against AI has started!', 'mode': 'ai', 'color': 'white'}, room=user_id)
    print(f"AI game started for user {user_id} with valid moves: {valid_moves}")

@socketio.on('join_multiplayer')
def handle_join_multiplayer():
    user_id = request.sid
    waiting_players.append(user_id)
    print(f"User {user_id} added to multiplayer queue.")

    # If two players are waiting, start a multiplayer game
    if len(waiting_players) >= 2:
        player1 = waiting_players.pop(0)
        player2 = waiting_players.pop(0)

        # Create a unique game ID
        game_id = str(uuid.uuid4())

        # Initialize a new GameState for the multiplayer game
        gs = GameState()
        multiplayer_games[game_id] = {
            'players': [player1, player2],
            'game_state': gs,
            'turn': 'white'  # White starts first
        }

        # Assign colors
        player_colors = {player1: 'white', player2: 'black'}

        # Join both players to a room identified by game_id
        join_room(game_id, player1)
        join_room(game_id, player2)

        # Emit initial game state to both players
        for player in [player1, player2]:
            emit('valid_moves', {
                'valid_moves': [
                    {'start_sq': [move.start_row, move.start_col], 'end_sq': [move.end_row, move.end_col]}
                    for move in gs.getValidMoves()
                ],
                'board': gs.board,
                'color': player_colors[player],
                'turn': 'white'
            }, room=player)

            emit('game_started', {
                'message': 'Multiplayer match has started!',
                'mode': 'multiplayer',
                'color': player_colors[player],
                'opponent': player2 if player == player1 else player1,
                'turn': 'white'
            }, room=player)

        print(f"Multiplayer game {game_id} started between {player1} (white) and {player2} (black).")

@socketio.on('make_move')
def handle_make_move(data):
    user_id = request.sid
    move_data = data.get('move')  # Data of the move sent by the client
    mode = data.get('mode')  # 'ai' or 'multiplayer'

    if mode == 'ai':
        # Handle single-player (AI) game moves
        gs = game_instances.get(user_id)
        if not gs:
            emit('error', {'message': 'Game state not found.'}, room=user_id)
            return

        player_move = Move(move_data['start_sq'], move_data['end_sq'], gs.board)

        if player_move in gs.getValidMoves():
            gs.makeMove(player_move)
            emit('move_made', {'move': player_move.getChessNotation(), 'board': gs.board}, room=user_id)

            # AI makes its move
            ai_move = findBestMove(gs, gs.getValidMoves())
            gs.makeMove(ai_move)
            emit('move_made', {'move': ai_move.getChessNotation(), 'board': gs.board}, room=user_id)

            # Send updated valid moves
            valid_moves = [
                {'start_sq': [move.start_row, move.start_col], 'end_sq': [move.end_row, move.end_col]}
                for move in gs.getValidMoves()
            ]
            emit('valid_moves', {'valid_moves': valid_moves, 'board': gs.board}, room=user_id)
        else:
            emit('invalid_move', {'message': 'Invalid move! Try again.'}, room=user_id)

        print(f"AI game move by user {user_id}: {player_move.getChessNotation()}")

    elif mode == 'multiplayer':
        # Handle multiplayer game moves
        game_id = None
        for gid, game in multiplayer_games.items():
            if user_id in game['players']:
                game_id = gid
                break

        if not game_id:
            emit('error', {'message': 'Multiplayer game not found.'}, room=user_id)
            return

        game = multiplayer_games[game_id]
        gs = game['game_state']
        current_turn = game['turn']
        player_index = game['players'].index(user_id)
        player_color = 'white' if player_index == 0 else 'black'

        if (current_turn == 'white' and player_color != 'white') or (current_turn == 'black' and player_color != 'black'):
            emit('invalid_move', {'message': 'Not your turn!'}, room=user_id)
            return

        player_move = Move(move_data['start_sq'], move_data['end_sq'], gs.board)

        if player_move in gs.getValidMoves():
            gs.makeMove(player_move)
            emit('move_made', {'move': player_move.getChessNotation(), 'board': gs.board}, room=game_id)

            # Toggle turn
            game['turn'] = 'black' if game['turn'] == 'white' else 'white'

            # Send updated valid moves and turn to both players
            valid_moves = [
                {'start_sq': [move.start_row, move.start_col], 'end_sq': [move.end_row, move.end_col]}
                for move in gs.getValidMoves()
            ]
            emit('valid_moves', {'valid_moves': valid_moves, 'board': gs.board, 'turn': game['turn']}, room=game_id)
        else:
            emit('invalid_move', {'message': 'Invalid move! Try again.'}, room=user_id)

        print(f"Multiplayer game {game_id} move by user {user_id}: {player_move.getChessNotation()}")

@socketio.on('hint')
def handle_hint(data):
    user_id = request.sid
    mode = data.get('mode')  # 'ai' or 'multiplayer'

    if mode == 'ai':
        # Provide hint in single-player (AI) game
        gs = game_instances.get(user_id)
        if not gs:
            emit('error', {'message': 'Game state not found.'}, room=user_id)
            return

        # Determine whose turn it is based on the board state
        white_to_move = gs.white_to_move

        # Get the best move (AI hint) for the current turn
        hint_move = findBestMove(gs, gs.getValidMoves())

        # Emit the AI hint move back to the user
        emit('hint_move', {'move': hint_move.getChessNotation(), 'white_to_move': white_to_move}, room=user_id)

        print(f"AI hint for user {user_id}: {hint_move.getChessNotation()}")

    elif mode == 'multiplayer':
        # Provide hint in multiplayer game
        game_id = None
        for gid, game in multiplayer_games.items():
            if user_id in game['players']:
                game_id = gid
                break

        if not game_id:
            emit('error', {'message': 'Multiplayer game not found.'}, room=user_id)
            return

        game = multiplayer_games[game_id]
        gs = game['game_state']
        current_turn = game['turn']

        # Get the best move (AI hint) for the current turn
        hint_move = findBestMove(gs, gs.getValidMoves())

        # Emit the AI hint move to both players
        emit('hint_move', {'move': hint_move.getChessNotation(), 'turn': current_turn}, room=game_id)

        print(f"Multiplayer game {game_id} hint: {hint_move.getChessNotation()}")

@socketio.on('disconnect')
def handle_disconnect():
    user_id = request.sid

    # Remove from AI game instances
    if user_id in game_instances:
        del game_instances[user_id]
        print(f"AI game removed for user {user_id}")

    # Remove from waiting multiplayer players
    if user_id in waiting_players:
        waiting_players.remove(user_id)
        print(f"User {user_id} removed from multiplayer queue.")

    # Remove from multiplayer games
    game_id_to_remove = None
    for gid, game in multiplayer_games.items():
        if user_id in game['players']:
            # Notify the other player
            other_player = game['players'][0] if game['players'][1] == user_id else game['players'][1]
            emit('opponent_disconnected', {'message': 'Your opponent has disconnected.'}, room=other_player)
            leave_room(gid, other_player)
            game_id_to_remove = gid
            break

    if game_id_to_remove:
        del multiplayer_games[game_id_to_remove]
        print(f"Multiplayer game {game_id_to_remove} ended due to disconnection of user {user_id}.")

    print(f"User disconnected: {user_id}")

if __name__ == '__main__':
    socketio.run(app, debug=True, port=5000)
    print("Server Running...")
