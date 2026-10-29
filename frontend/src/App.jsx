import { useCallback, useEffect, useMemo, useState } from 'react';
import GameBoard from './components/GameBoard';
import GamePanel from './components/GamePanel';
import NewGamePanel from './components/NewGamePanel';
import PlayerBar from './components/PlayerBar';
import { useChessGame } from './hooks/useChessGame';
import { START_BOARD, capturedMaterial } from './lib/board';

export default function App() {
  const { state, startGame, leaveGame, makeMove, requestHint, dismissNotice } = useChessGame();
  const { phase, mode, color, turn, connected, notice } = state;
  const [flipped, setFlipped] = useState(false);

  const inGame = phase === 'playing' || phase === 'over';
  const board = state.board || START_BOARD;
  const myColor = inGame ? color : 'white';
  const orientation = flipped ? (myColor === 'white' ? 'black' : 'white') : myColor;
  const theirColor = myColor === 'white' ? 'black' : 'white';
  const interactive = phase === 'playing' && turn === color && !state.pending;

  const { captured, balance } = useMemo(() => capturedMaterial(board), [board]);
  const advantage = (side) => Math.max(0, side === 'white' ? balance : -balance);

  const waiting = phase === 'waiting';
  useEffect(() => setFlipped(false), [color, waiting]);

  useEffect(() => {
    if (!notice) return undefined;
    const timer = setTimeout(dismissNotice, 3500);
    return () => clearTimeout(timer);
  }, [notice, dismissNotice]);

  const handleLeave = useCallback(() => {
    if (phase === 'playing' && !window.confirm('Leave the current game?')) return;
    leaveGame();
  }, [phase, leaveGame]);

  const opponent = {
    name: !inGame ? 'Opponent' : mode === 'ai' ? 'Engine' : 'Opponent',
    detail: !inGame ? null : mode === 'ai' ? 'NegaMax · depth 3' : 'Online',
  };

  const bars = {
    [myColor]: { name: 'You', detail: inGame ? `Playing ${myColor}` : null },
    [theirColor]: opponent,
  };
  const topColor = orientation === 'white' ? 'black' : 'white';
  const bottomColor = orientation;

  const renderBar = (side) => (
    <PlayerBar
      {...bars[side]}
      color={side}
      captured={captured[side[0]]}
      advantage={advantage(side)}
      active={phase === 'playing' && turn === side}
    />
  );

  return (
    <div className="app d-flex flex-column min-vh-100">
      <header className="app-header">
        <div className="container d-flex align-items-center py-3">
          <span className="brand me-auto">
            <span className="brand-mark" aria-hidden="true">♞</span>
            Chess Engine
          </span>
          <span className={`conn ${connected ? 'is-online' : ''}`}>
            <span className="conn-dot" aria-hidden="true" />
            {connected ? 'Server online' : 'Connecting…'}
          </span>
        </div>
      </header>

      <main className="container flex-grow-1 py-4">
        <div className="row g-4 justify-content-center">
          <section className="col-lg-7 col-xl-6" aria-label="Board">
            {renderBar(topColor)}
            <GameBoard
              board={board}
              validMoves={state.validMoves}
              orientation={orientation}
              interactive={interactive}
              lastMove={state.lastMove}
              hint={state.hint}
              result={state.result}
              onMove={makeMove}
            />
            {renderBar(bottomColor)}
          </section>

          <aside className="col-lg-5 col-xl-4">
            {inGame ? (
              <GamePanel
                state={state}
                onHint={requestHint}
                onFlip={() => setFlipped((f) => !f)}
                onNewGame={() => startGame(mode)}
                onLeave={handleLeave}
              />
            ) : (
              <NewGamePanel
                connected={connected}
                waiting={phase === 'waiting'}
                mode={mode}
                onStart={startGame}
                onCancel={leaveGame}
              />
            )}

            {notice && (
              <div className="alert alert-warning small d-flex align-items-center mt-3 mb-0 py-2" role="alert">
                <span className="me-auto">{notice}</span>
                <button type="button" className="btn-close btn-sm" aria-label="Dismiss" onClick={dismissNotice} />
              </div>
            )}
          </aside>
        </div>
      </main>

      <footer className="app-footer">
        <div className="container py-3 small text-secondary">
          Custom move generator and NegaMax search with alpha-beta pruning, served over Socket.IO.
        </div>
      </footer>
    </div>
  );
}
