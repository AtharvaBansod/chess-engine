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

  if (waiting) {
    return (
      <div className="panel p-4 text-center">
        <div className="spinner-border spinner-border-sm text-accent mb-3" role="status" />
        <h2 className="h6 mb-1">{mode === 'ai' ? 'Setting up the board' : 'Looking for an opponent'}</h2>
        <p className="small text-secondary mb-3">
          {mode === 'ai' ? 'Connecting to the engine…' : 'The game starts as soon as another player joins.'}
        </p>
        <button type="button" className="btn btn-sm btn-outline-secondary" onClick={onCancel}>
          Cancel
        </button>
      </div>
    );
  }

  return (
    <div className="panel">
      <div className="panel-header">New game</div>
      <div className="p-3">
        <div className="d-grid gap-2 mb-3" role="radiogroup" aria-label="Game mode">
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
        <button
          type="button"
          className="btn btn-accent w-100"
          disabled={!connected}
          onClick={() => onStart(choice)}
        >
          Start game
        </button>
        {!connected && (
          <p className="small text-secondary mt-2 mb-0">Waiting for the server to come online.</p>
        )}
      </div>
    </div>
  );
}
