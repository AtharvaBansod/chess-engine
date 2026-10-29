import { useCallback, useEffect, useReducer, useRef } from 'react';
import { io } from 'socket.io-client';
import { applyMove, fromSquare, parseMove } from '../lib/board';

const SERVER_URL = import.meta.env.VITE_SERVER_URL || 'http://localhost:5000';

const initialState = {
  connected: false,
  phase: 'idle', // idle | waiting | playing | over
  mode: null, // 'ai' | 'multiplayer'
  color: 'white',
  turn: 'white',
  board: null,
  serverBoard: null,
  validMoves: [],
  history: [],
  lastMove: null,
  hint: null,
  hintLoading: false,
  pending: false,
  result: null,
  notice: null,
};

const other = (color) => (color === 'white' ? 'black' : 'white');

function reducer(state, action) {
  switch (action.type) {
    case 'connection':
      return {
        ...state,
        connected: action.connected,
        ...(!action.connected && state.phase === 'playing'
          ? { phase: 'over', result: { kind: 'lost-connection' } }
          : {}),
      };

    case 'start':
      return {
        ...initialState,
        connected: state.connected,
        phase: action.mode ? 'waiting' : 'idle',
        mode: action.mode,
      };

    case 'game_started':
      return {
        ...state,
        phase: 'playing',
        mode: action.data.mode,
        color: action.data.color || 'white',
        turn: action.data.turn || 'white',
      };

    case 'valid_moves': {
      const { data } = action;
      const turn = data.turn || 'white';
      const next = {
        ...state,
        board: data.board,
        serverBoard: data.board,
        validMoves: data.valid_moves,
        color: data.color || state.color,
        turn,
        pending: false,
      };
      if (data.valid_moves.length === 0 && state.phase === 'playing') {
        next.phase = 'over';
        next.result = data.stalemate
          ? { kind: 'stalemate' }
          : { kind: 'checkmate', winner: other(turn), loser: turn };
      }
      return next;
    }

    case 'local_move':
      return {
        ...state,
        board: applyMove(state.board, action.from, action.to),
        lastMove: { from: action.from, to: action.to },
        validMoves: [],
        hint: null,
        pending: true,
      };

    case 'move_made':
      return {
        ...state,
        board: action.data.board,
        serverBoard: action.data.board,
        history: [...state.history, action.data.move],
        lastMove: parseMove(action.data.move),
        turn: other(state.turn),
        hint: null,
      };

    case 'rejected':
      return {
        ...state,
        board: state.serverBoard,
        pending: false,
        hintLoading: false,
        notice: action.message,
      };

    case 'hint_request':
      return { ...state, hintLoading: true, hint: null };

    case 'hint_move':
      // In online games the server broadcasts hints to the room; only the side to move uses it.
      return {
        ...state,
        hintLoading: false,
        hint: state.turn === state.color ? parseMove(action.data.move) : state.hint,
      };

    case 'opponent_left':
      return { ...state, phase: 'over', result: state.result || { kind: 'abandoned' } };

    case 'dismiss_notice':
      return { ...state, notice: null };

    default:
      return state;
  }
}

export function useChessGame() {
  const [state, dispatch] = useReducer(reducer, initialState);
  const socketRef = useRef(null);
  const stateRef = useRef(state);
  stateRef.current = state;

  useEffect(() => {
    const socket = io(SERVER_URL, { transports: ['websocket', 'polling'] });
    socketRef.current = socket;

    socket.on('connect', () => dispatch({ type: 'connection', connected: true }));
    socket.on('disconnect', () => dispatch({ type: 'connection', connected: false }));
    socket.on('game_started', (data) => dispatch({ type: 'game_started', data }));
    socket.on('valid_moves', (data) => dispatch({ type: 'valid_moves', data }));
    socket.on('move_made', (data) => dispatch({ type: 'move_made', data }));
    socket.on('hint_move', (data) => dispatch({ type: 'hint_move', data }));
    socket.on('invalid_move', (data) => dispatch({ type: 'rejected', message: data.message }));
    socket.on('error', (data) => dispatch({ type: 'rejected', message: data?.message || 'Server error.' }));
    socket.on('opponent_disconnected', () => dispatch({ type: 'opponent_left' }));

    return () => socket.disconnect();
  }, []);

  // A fresh connection gives the server a clean slate: its disconnect handler
  // drops us from the matchmaking queue and from any running game.
  const resetConnection = useCallback(() => {
    const socket = socketRef.current;
    if (stateRef.current.phase !== 'idle') {
      socket.disconnect();
      socket.connect();
    }
    return socket;
  }, []);

  const startGame = useCallback(
    (mode) => {
      const socket = resetConnection();
      dispatch({ type: 'start', mode });
      socket.emit(mode === 'ai' ? 'join_game' : 'join_multiplayer');
    },
    [resetConnection]
  );

  const leaveGame = useCallback(() => {
    resetConnection();
    dispatch({ type: 'start', mode: null });
  }, [resetConnection]);

  const makeMove = useCallback((from, to) => {
    dispatch({ type: 'local_move', from, to });
    socketRef.current.emit('make_move', {
      mode: stateRef.current.mode,
      move: { start_sq: fromSquare(from), end_sq: fromSquare(to) },
    });
  }, []);

  const requestHint = useCallback(() => {
    dispatch({ type: 'hint_request' });
    socketRef.current.emit('hint', { mode: stateRef.current.mode });
  }, []);

  const dismissNotice = useCallback(() => dispatch({ type: 'dismiss_notice' }), []);

  return { state, startGame, leaveGame, makeMove, requestHint, dismissNotice, serverUrl: SERVER_URL };
}
