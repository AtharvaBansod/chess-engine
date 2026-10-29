import KingIcon from './KingIcon';

const GLYPHS = { p: '♟', N: '♞', B: '♝', R: '♜', Q: '♛' };

export default function PlayerBar({ name, detail, color, captured, advantage, active, thinking }) {
  return (
    <div className={`player-bar ${active ? 'is-active' : ''}`}>
      <span className={`player-avatar avatar-${color}`}>
        <KingIcon color={color} size={26} />
      </span>
      <div className="lh-sm me-auto text-truncate">
        <div className="fw-semibold">{name}</div>
        {detail && <div className="small text-secondary">{detail}</div>}
      </div>
      <div className="captured text-secondary" aria-label="Captured pieces">
        {captured.map((piece, i) => (
          <span key={i}>{GLYPHS[piece[1]]}</span>
        ))}
        {advantage > 0 && <span className="ms-1 small fw-semibold">+{advantage}</span>}
      </div>
      {active && (
        <span className="turn-pill">
          {thinking && <span className="spinner-grow spinner-grow-sm" aria-hidden="true" />}
          {thinking ? 'Thinking' : 'To move'}
        </span>
      )}
    </div>
  );
}
