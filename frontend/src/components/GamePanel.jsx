import MoveList from './MoveList';

const cap = (s) => s.charAt(0).toUpperCase() + s.slice(1);

function describeResult(result, color) {
  switch (result?.kind) {
    case 'checkmate':
      return {
        title: result.winner === color ? 'You won' : 'You lost',
        text: `Checkmate — ${cap(result.winner)} wins.`,
      };
    case 'stalemate':
      return { title: 'Draw', text: 'Stalemate. No legal moves remain.' };
    case 'abandoned':
      return { title: 'Game ended', text: 'Your opponent disconnected.' };
    case 'lost-connection':
      return { title: 'Connection lost', text: 'The server closed the connection.' };
    default:
      return null;
  }
}

function statusLine({ phase, mode, turn, color, pending }) {
  if (phase === 'over') return null;
  if (turn === color) return pending ? 'Sending move…' : 'Your move';
  return mode === 'ai' ? 'Engine is thinking…' : 'Waiting for opponent…';
}

export default function GamePanel({ state, onHint, onFlip, onNewGame, onLeave }) {
  const { phase, mode, turn, color, history, hintLoading, result } = state;
  const outcome = describeResult(result, color);
  const status = statusLine(state);
  const myTurn = phase === 'playing' && turn === color && !state.pending;
  const thinking = status && turn !== color;

  return (
    <div className="panel d-flex flex-column">
      <div className="panel-header d-flex align-items-center">
        <span className="me-auto">{mode === 'ai' ? 'vs Engine' : 'Online game'}</span>
        <span className="text-secondary fw-normal small">Playing {color}</span>
      </div>

      {outcome ? (
        <div className="result px-3 py-3 border-bottom">
          <div className="fw-semibold">{outcome.title}</div>
          <div className="small text-secondary">{outcome.text}</div>
        </div>
      ) : (
        <div className="px-3 py-2 border-bottom d-flex align-items-center gap-2 small">
          {thinking ? (
            <span className="spinner-grow spinner-grow-sm text-secondary" aria-hidden="true" />
          ) : (
            <span className="turn-dot" aria-hidden="true" />
          )}
          <span>{status}</span>
        </div>
      )}

      <MoveList moves={history} />

      <div className="p-3 border-top d-flex flex-wrap gap-2">
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
