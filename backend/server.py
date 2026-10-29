import copy
import threading
import uuid

from flask import Flask, request
from flask_cors import CORS
from flask_socketio import SocketIO, emit, join_room, leave_room

from ChessEngine2 import GameState
from minMax import HINT_TIME, SEARCH_TIME, SearchCancelled, findBestMove

app = Flask(__name__)
CORS(app)
socketio = SocketIO(app, cors_allowed_origins="*", manage_session=False)

game_instances = {}
multiplayer_games = {}
waiting_players = []
game_locks = {}
hint_searches = {}


def color_to_move(gs):
    return 'white' if gs.white_to_move else 'black'


def is_game_over(gs, valid_moves):
    return not valid_moves or gs.isThreefoldRepetition()


def state_payload(gs, valid_moves, **extra):
    repetition = gs.isThreefoldRepetition()
    payload = {
        'valid_moves': [] if repetition else [
            {'start_sq': [m.start_row, m.start_col], 'end_sq': [m.end_row, m.end_col]}
            for m in valid_moves
        ],
        'board': gs.board,
        'turn': color_to_move(gs),
        'checkmate': gs.checkmate and not repetition,
        'stalemate': gs.stalemate and not repetition,
        'repetition': repetition,
    }
    payload.update(extra)
    return payload


def match_valid_move(gs, move_data):
    try:
        start = (int(move_data['start_sq'][0]), int(move_data['start_sq'][1]))
        end = (int(move_data['end_sq'][0]), int(move_data['end_sq'][1]))
    except (KeyError, IndexError, TypeError, ValueError):
        return None
    for move in gs.getValidMoves():
        if (move.start_row, move.start_col) == start and (move.end_row, move.end_col) == end:
            return move
    return None


def cancel_hint(user_id):
    event = hint_searches.pop(user_id, None)
    if event is not None:
        event.set()


def find_multiplayer_game(user_id):
    for game_id, game in multiplayer_games.items():
        if user_id in game['players']:
            return game_id, game
    return None, None


@app.route('/')
def home():
    return "Chess Server!"


@socketio.on('connect')
def handle_connect():
    print(f"User connected: {request.sid}")


@socketio.on('join_game')
def handle_join_game():
    user_id = request.sid
    cancel_hint(user_id)
    gs = GameState()
    game_instances[user_id] = gs
    game_locks[user_id] = threading.Lock()
    emit('valid_moves', state_payload(gs, gs.getValidMoves(), color='white'), room=user_id)
    emit('game_started', {'message': 'Game against AI has started!', 'mode': 'ai', 'color': 'white',
                          'turn': 'white'}, room=user_id)


@socketio.on('join_multiplayer')
def handle_join_multiplayer():
    user_id = request.sid
    if user_id in waiting_players:
        return
    waiting_players.append(user_id)

    if len(waiting_players) < 2:
        return

    player1 = waiting_players.pop(0)
    player2 = waiting_players.pop(0)
    game_id = str(uuid.uuid4())
    gs = GameState()
    multiplayer_games[game_id] = {'players': [player1, player2], 'game_state': gs}
    game_locks[game_id] = threading.Lock()
    join_room(game_id, player1)
    join_room(game_id, player2)

    valid_moves = gs.getValidMoves()
    for player, color in ((player1, 'white'), (player2, 'black')):
        emit('valid_moves', state_payload(gs, valid_moves, color=color), room=player)
        emit('game_started', {
            'message': 'Multiplayer match has started!',
            'mode': 'multiplayer',
            'color': color,
            'opponent': player2 if player == player1 else player1,
            'turn': 'white',
        }, room=player)


def play_ai_move(user_id, move_data):
    gs = game_instances.get(user_id)
    if not gs:
        emit('error', {'message': 'Game state not found.'}, room=user_id)
        return

    with game_locks[user_id]:
        if gs.isThreefoldRepetition():
            emit('invalid_move', {'message': 'The game is over.'}, room=user_id)
            return
        if not gs.white_to_move:
            emit('invalid_move', {'message': 'Wait for the engine to move.'}, room=user_id)
            return
        player_move = match_valid_move(gs, move_data)
        if player_move is None:
            emit('invalid_move', {'message': 'Invalid move! Try again.'}, room=user_id)
            emit('valid_moves', state_payload(gs, gs.getValidMoves()), room=user_id)
            return

        gs.makeMove(player_move)
        emit('move_made', {'move': player_move.getChessNotation(), 'board': gs.board}, room=user_id)

        ai_replies = gs.getValidMoves()
        if is_game_over(gs, ai_replies):
            emit('valid_moves', state_payload(gs, []), room=user_id)
            return

        ai_move = findBestMove(gs, ai_replies, time_limit=SEARCH_TIME) or ai_replies[0]
        gs.makeMove(ai_move)
        emit('move_made', {'move': ai_move.getChessNotation(), 'board': gs.board}, room=user_id)
        emit('valid_moves', state_payload(gs, gs.getValidMoves()), room=user_id)


def play_multiplayer_move(user_id, move_data):
    game_id, game = find_multiplayer_game(user_id)
    if not game:
        emit('error', {'message': 'Multiplayer game not found.'}, room=user_id)
        return

    with game_locks[game_id]:
        gs = game['game_state']
        player_color = 'white' if game['players'][0] == user_id else 'black'
        if gs.isThreefoldRepetition():
            emit('invalid_move', {'message': 'The game is over.'}, room=user_id)
            return
        if color_to_move(gs) != player_color:
            emit('invalid_move', {'message': 'Not your turn!'}, room=user_id)
            return

        player_move = match_valid_move(gs, move_data)
        if player_move is None:
            emit('invalid_move', {'message': 'Invalid move! Try again.'}, room=user_id)
            emit('valid_moves', state_payload(gs, gs.getValidMoves()), room=user_id)
            return

        gs.makeMove(player_move)
        emit('move_made', {'move': player_move.getChessNotation(), 'board': gs.board}, room=game_id)
        emit('valid_moves', state_payload(gs, gs.getValidMoves()), room=game_id)


@socketio.on('make_move')
def handle_make_move(data):
    user_id = request.sid
    cancel_hint(user_id)
    data = data or {}
    if data.get('mode') == 'multiplayer':
        play_multiplayer_move(user_id, data.get('move'))
    else:
        play_ai_move(user_id, data.get('move'))


@socketio.on('cancel_hint')
def handle_cancel_hint():
    cancel_hint(request.sid)


@socketio.on('hint')
def handle_hint(data):
    user_id = request.sid
    mode = (data or {}).get('mode')

    if mode == 'multiplayer':
        game_id, game = find_multiplayer_game(user_id)
        gs = game['game_state'] if game else None
        lock = game_locks.get(game_id)
    else:
        gs = game_instances.get(user_id)
        lock = game_locks.get(user_id)

    if not gs or not lock:
        emit('error', {'message': 'Game state not found.'}, room=user_id)
        return

    with lock:
        snapshot = copy.deepcopy(gs)
    candidates = snapshot.getValidMoves()
    if is_game_over(snapshot, candidates):
        return

    cancel_hint(user_id)
    stop = threading.Event()
    hint_searches[user_id] = stop
    try:
        hint_move = findBestMove(snapshot, candidates, should_stop=stop.is_set,
                                   time_limit=HINT_TIME) or candidates[0]
    except SearchCancelled:
        return
    finally:
        if hint_searches.get(user_id) is stop:
            del hint_searches[user_id]

    if not stop.is_set():
        emit('hint_move', {'move': hint_move.getChessNotation(), 'turn': color_to_move(snapshot)}, room=user_id)


@socketio.on('disconnect')
def handle_disconnect():
    user_id = request.sid
    cancel_hint(user_id)
    game_instances.pop(user_id, None)
    game_locks.pop(user_id, None)

    if user_id in waiting_players:
        waiting_players.remove(user_id)

    game_id, game = find_multiplayer_game(user_id)
    if game:
        other_player = next(p for p in game['players'] if p != user_id)
        emit('opponent_disconnected', {'message': 'Your opponent has disconnected.'}, room=other_player)
        leave_room(game_id, other_player)
        del multiplayer_games[game_id]
        game_locks.pop(game_id, None)

    print(f"User disconnected: {user_id}")


if __name__ == '__main__':
    socketio.run(app, debug=True, port=5000)
