import MoveList from './MoveList';

const cap = (s) => s.charAt(0).toUpperCase() + s.slice(1);

function describeResult(result, color) {
  switch (result?.kind) {
    case 'checkmate':
      return {
        title: result.winner === color ? 'You won' : 'You lost',
        text: `Checkmate. ${cap(result.winner)} wins.`,
      };
    case 'stalemate':
      return { title: 'Draw', text: 'Stalemate. No legal moves remain.' };
    case 'repetition':
      return { title: 'Draw', text: 'Threefold repetition. The same position occurred three times.' };
    case 'abandoned':
      return { title: 'Game ended', text: 'Your opponent disconnected.' };
    case 'lost-connection':
      return { title: 'Connection lost', text: 'The server closed the connection.' };
    default:
      return null;
  }
}

function statusLine({ mode, turn, color, pending, hintLoading }) {
  if (turn === color) {
    if (pending) return 'Sending move…';
    return hintLoading ? 'Finding the best move…' : 'Your move';
  }
  return mode === 'ai' ? 'Engine is thinking…' : 'Waiting for your opponent…';
}

export default function GamePanel({ state, onHint, onFlip, onNewGame, onLeave }) {
  const { phase, mode, turn, color, history, hintLoading, result } = state;
  const outcome = describeResult(result, color);
  const myTurn = phase === 'playing' && turn === color && !state.pending;
  const busy = phase === 'playing' && (turn !== color || hintLoading);

  return (
    <div className="panel">
      <div className="panel-header d-flex align-items-center">
        <span className="me-auto">{mode === 'ai' ? 'vs Engine' : 'Online game'}</span>
        <span className="text-secondary fw-normal small">Playing {color}</span>
      </div>

      {outcome ? (
        <div className="status-row result">
          <div className="fw-semibold">{outcome.title}</div>
          <div className="small text-secondary">{outcome.text}</div>
        </div>
      ) : (
        <div className="status-row d-flex align-items-center gap-2 small">
          {busy ? (
            <span className="spinner-grow spinner-grow-sm text-secondary" aria-hidden="true" />
          ) : (
            <span className="turn-dot" aria-hidden="true" />
          )}
          <span>{statusLine(state)}</span>
        </div>
      )}

      <div className="panel-label">Moves</div>
      <MoveList moves={history} />

      <div className="panel-footer d-flex flex-wrap gap-2">
        {phase === 'playing' && (
          <button
            type="button"
            className="btn btn-sm btn-outline-secondary"
            disabled={!myTurn || hintLoading}
            onClick={onHint}
          >
            {hintLoading ? (
              <span className="spinner-border spinner-border-sm me-1" aria-hidden="true" />
            ) : (
              <i className="bi bi-lightbulb me-1" aria-hidden="true" />
            )}
            Hint
          </button>
        )}
        <button type="button" className="btn btn-sm btn-outline-secondary" onClick={onFlip}>
          <i className="bi bi-arrow-down-up me-1" aria-hidden="true" />
          Flip
        </button>
        <div className="ms-auto d-flex gap-2">
          {phase === 'over' ? (
            <>
              <button type="button" className="btn btn-sm btn-outline-secondary" onClick={onLeave}>
                Close
              </button>
              <button type="button" className="btn btn-sm btn-accent" onClick={onNewGame}>
                Play again
              </button>
            </>
          ) : (
            <button type="button" className="btn btn-sm btn-outline-danger" onClick={onLeave}>
              Leave game
            </button>
          )}
        </div>
      </div>
    </div>
  );
}
