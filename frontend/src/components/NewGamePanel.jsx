import { useState } from 'react';

const MODES = [
  {
    id: 'ai',
    icon: 'bi-cpu',
    title: 'Play the engine',
    text: 'You take white. NegaMax search with alpha-beta pruning replies.',
  },
  {
    id: 'multiplayer',
    icon: 'bi-people',
    title: 'Play online',
    text: 'Get paired with the next player who joins the queue.',
  },
];

export default function NewGamePanel({ connected, waiting, mode, onStart, onCancel }) {
  const [choice, setChoice] = useState('ai');

  return (
    <div className="panel">
      <div className="panel-header">New game</div>

      {waiting ? (
        <div className="panel-body d-flex flex-column align-items-center justify-content-center text-center">
          <div className="spinner-border spinner-border-sm text-accent mb-3" role="status" />
          <h2 className="h6 mb-1">{mode === 'ai' ? 'Setting up the board' : 'Looking for an opponent'}</h2>
          <p className="small text-secondary mb-3">
            {mode === 'ai' ? 'Connecting to the engine…' : 'The game starts as soon as another player joins.'}
          </p>
          <button type="button" className="btn btn-sm btn-outline-secondary" onClick={onCancel}>
            Cancel
          </button>
        </div>
      ) : (
        <div className="panel-body p-3 d-flex flex-column">
          <div className="d-grid gap-2" role="radiogroup" aria-label="Game mode">
            {MODES.map((m) => (
              <button
                key={m.id}
                type="button"
                role="radio"
                aria-checked={choice === m.id}
                className={`mode-option ${choice === m.id ? 'is-selected' : ''}`}
                onClick={() => setChoice(m.id)}
              >
                <i className={`bi ${m.icon}`} aria-hidden="true" />
                <span>
                  <span className="d-block fw-semibold">{m.title}</span>
                  <span className="d-block small text-secondary">{m.text}</span>
                </span>
              </button>
            ))}
          </div>

          <dl className="engine-facts small mt-auto mb-0">
            <div>
              <dt>Search</dt>
              <dd>NegaMax, alpha-beta</dd>
            </div>
            <div>
              <dt>Depth</dt>
              <dd>3+ plies, iterative</dd>
            </div>
            <div>
              <dt>Evaluation</dt>
              <dd>Material and piece-square tables</dd>
            </div>
          </dl>
        </div>
      )}

      {!waiting && (
        <div className="panel-footer">
          <button
            type="button"
            className="btn btn-accent w-100"
            disabled={!connected}
            onClick={() => onStart(choice)}
          >
            {connected ? 'Start game' : 'Waiting for server…'}
          </button>
        </div>
      )}
    </div>
  );
}
