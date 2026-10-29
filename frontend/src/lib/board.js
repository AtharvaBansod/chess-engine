// Helpers for translating between the backend's 8x8 array and algebraic squares.
// Backend rows run 0..7 from rank 8 down to rank 1; pieces look like "wK", "bp", "--".

const FILES = 'abcdefgh';

const BACK_RANK = ['R', 'N', 'B', 'Q', 'K', 'B', 'N', 'R'];
export const START_BOARD = [
  BACK_RANK.map((p) => `b${p}`),
  Array(8).fill('bp'),
  ...Array.from({ length: 4 }, () => Array(8).fill('--')),
  Array(8).fill('wp'),
  BACK_RANK.map((p) => `w${p}`),
];

export const toSquare = (row, col) => `${FILES[col]}${8 - row}`;

export const fromSquare = (square) => [8 - Number(square[1]), FILES.indexOf(square[0])];

/** Board array -> react-chessboard position object, e.g. { e2: 'wP' }. */
export function toPosition(board) {
  const position = {};
  if (!board) return position;
  board.forEach((rank, row) =>
    rank.forEach((piece, col) => {
      if (piece && piece !== '--') {
        position[toSquare(row, col)] = piece[0] + piece[1].toUpperCase();
      }
    })
  );
  return position;
}

/** Backend move list -> Map of "e2" -> Set(["e3", "e4"]). */
export function indexMoves(validMoves = []) {
  const map = new Map();
  for (const { start_sq: s, end_sq: e } of validMoves) {
    const from = toSquare(s[0], s[1]);
    if (!map.has(from)) map.set(from, new Set());
    map.get(from).add(toSquare(e[0], e[1]));
  }
  return map;
}

/** "e2e4" -> { from: "e2", to: "e4" } */
export function parseMove(notation) {
  if (!notation || notation.length < 4) return null;
  return { from: notation.slice(0, 2), to: notation.slice(2, 4) };
}

/** Find the king of the given colour ("w" | "b") on the board. */
export function findKing(board, colour) {
  if (!board) return null;
  for (let r = 0; r < 8; r++) {
    for (let c = 0; c < 8; c++) {
      if (board[r][c] === `${colour}K`) return toSquare(r, c);
    }
  }
  return null;
}

/**
 * Apply a move locally so the board responds instantly; the server's board
 * replaces this as soon as it arrives. Covers castling, en passant and
 * promotion (the engine always promotes to a queen).
 */
export function applyMove(board, from, to) {
  const next = board.map((rank) => rank.slice());
  const [fr, fc] = fromSquare(from);
  const [tr, tc] = fromSquare(to);
  const piece = next[fr][fc];

  if (piece[1] === 'p' && fc !== tc && next[tr][tc] === '--') next[fr][tc] = '--';
  if (piece[1] === 'K' && Math.abs(tc - fc) === 2) {
    const rookFrom = tc > fc ? 7 : 0;
    const rookTo = tc > fc ? tc - 1 : tc + 1;
    next[fr][rookTo] = next[fr][rookFrom];
    next[fr][rookFrom] = '--';
  }

  next[tr][tc] = piece[1] === 'p' && (tr === 0 || tr === 7) ? `${piece[0]}Q` : piece;
  next[fr][fc] = '--';
  return next;
}

const START_COUNT = { p: 8, N: 2, B: 2, R: 2, Q: 1 };
const VALUES = { p: 1, N: 3, B: 3, R: 5, Q: 9 };

/** Pieces each side has captured, plus the material balance from white's view. */
export function capturedMaterial(board) {
  const count = { w: {}, b: {} };
  board?.flat().forEach((piece) => {
    if (piece !== '--') count[piece[0]][piece[1]] = (count[piece[0]][piece[1]] || 0) + 1;
  });

  const captured = { w: [], b: [] }; // captured.w = black pieces taken by white
  let balance = 0;
  for (const type of Object.keys(START_COUNT)) {
    const missingBlack = Math.max(0, START_COUNT[type] - (count.b[type] || 0));
    const missingWhite = Math.max(0, START_COUNT[type] - (count.w[type] || 0));
    for (let i = 0; i < missingBlack; i++) captured.w.push(`b${type}`);
    for (let i = 0; i < missingWhite; i++) captured.b.push(`w${type}`);
    balance += (missingBlack - missingWhite) * VALUES[type];
  }
  return { captured, balance };
}
