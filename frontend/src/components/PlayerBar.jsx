const GLYPHS = { p: '♟', N: '♞', B: '♝', R: '♜', Q: '♛' };

export default function PlayerBar({ name, detail, color, captured, advantage, active }) {
  return (
    <div className={`player-bar d-flex align-items-center gap-2 ${active ? 'is-active' : ''}`}>
      <span className={`swatch swatch-${color}`} aria-hidden="true" />
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
      {active && <span className="turn-dot" title="To move" />}
    </div>
  );
}
