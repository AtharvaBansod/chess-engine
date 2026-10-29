import { useCallback, useEffect, useReducer, useRef } from 'react';
import { io } from 'socket.io-client';
import { applyMove, fromSquare, parseMove } from '../lib/board';

const SERVER_URL = import.meta.env.VITE_SERVER_URL || 'http://localhost:5000';

let sharedSocket = null;
const getSocket = () => {
  if (!sharedSocket) {
    sharedSocket = io(SERVER_URL, { transports: ['websocket', 'polling'], autoConnect: false });
  }
  return sharedSocket;
};

const initialState = {
  connected: false,
  phase: 'idle',
  mode: null,
  color: 'white',
  turn: 'white',
  board: null,
  serverBoard: null,
  validMoves: [],
  serverValidMoves: [],
  history: [],
  lastMove: null,
  serverLastMove: null,
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
          ? { phase: 'over', result: { kind: 'lost-connection' }, pending: false, hintLoading: false }
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
        color: action.data.color || state.color,
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
        serverValidMoves: data.valid_moves,
        lastMove: state.serverLastMove,
        color: data.color || state.color,
        turn,
        pending: false,
      };
      if (data.valid_moves.length === 0 && state.phase === 'playing') {
        next.phase = 'over';
        next.hintLoading = false;
        if (data.repetition) next.result = { kind: 'repetition' };
        else if (data.stalemate) next.result = { kind: 'stalemate' };
        else next.result = { kind: 'checkmate', winner: other(turn), loser: turn };
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
        hintLoading: false,
        pending: true,
      };

    case 'move_made': {
      const lastMove = parseMove(action.data.move);
      return {
        ...state,
        board: action.data.board,
        serverBoard: action.data.board,
        history: [...state.history, action.data.move],
        lastMove,
        serverLastMove: lastMove,
        turn: other(state.turn),
        hint: null,
      };
    }

    case 'rejected':
      return {
        ...state,
        board: state.serverBoard,
        validMoves: state.serverValidMoves,
        lastMove: state.serverLastMove,
        pending: false,
        hintLoading: false,
        notice: action.message,
      };

    case 'hint_request':
      return { ...state, hintLoading: true, hint: null };

    case 'hint_move':
      if (!state.hintLoading || state.turn !== state.color) return state;
      return { ...state, hintLoading: false, hint: parseMove(action.data.move) };

    case 'opponent_left':
      return {
        ...state,
        phase: 'over',
        pending: false,
        hintLoading: false,
        result: state.result || { kind: 'abandoned' },
      };

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
    const socket = getSocket();
    socketRef.current = socket;

    const handlers = {
      connect: () => dispatch({ type: 'connection', connected: true }),
      disconnect: () => dispatch({ type: 'connection', connected: false }),
      game_started: (data) => dispatch({ type: 'game_started', data }),
      valid_moves: (data) => dispatch({ type: 'valid_moves', data }),
      move_made: (data) => dispatch({ type: 'move_made', data }),
      hint_move: (data) => dispatch({ type: 'hint_move', data }),
      invalid_move: (data) => dispatch({ type: 'rejected', message: data.message }),
      error: (data) => dispatch({ type: 'rejected', message: data?.message || 'Server error.' }),
      opponent_disconnected: () => dispatch({ type: 'opponent_left' }),
    };

    Object.entries(handlers).forEach(([event, handler]) => socket.on(event, handler));
    if (socket.connected) dispatch({ type: 'connection', connected: true });
    else socket.connect();

    return () => Object.entries(handlers).forEach(([event, handler]) => socket.off(event, handler));
  }, []);

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

  return { state, startGame, leaveGame, makeMove, requestHint, dismissNotice };
}
