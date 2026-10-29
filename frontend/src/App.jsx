import { useCallback, useEffect, useMemo, useState } from 'react';
import GameBoard from './components/GameBoard';
import GamePanel from './components/GamePanel';
import NewGamePanel from './components/NewGamePanel';
import PlayerBar from './components/PlayerBar';
import { useChessGame } from './hooks/useChessGame';
import { useElementSize } from './hooks/useElementSize';
import { START_BOARD, capturedMaterial } from './lib/board';

const BAR_HEIGHT = 56;
const FRAME = 14;
const PANEL_WIDTH = 360;
const GAP = 24;
const WIDE_BREAKPOINT = 992;

function computeBoardSize({ width, height }) {
  if (!width) return 0;
  if (width < WIDE_BREAKPOINT - 48) return Math.max(240, width - FRAME);
  const byHeight = height - 2 * BAR_HEIGHT - FRAME;
  const byWidth = width - PANEL_WIDTH - GAP - FRAME;
  return Math.max(280, Math.floor(Math.min(byHeight, byWidth)));
}

export default function App() {
  const { state, startGame, leaveGame, makeMove, requestHint, dismissNotice } = useChessGame();
  const { phase, mode, color, turn, connected, notice } = state;
  const [flipped, setFlipped] = useState(false);
  const [areaRef, area] = useElementSize();

  const inGame = phase === 'playing' || phase === 'over';
  const waiting = phase === 'waiting';
  const board = state.board || START_BOARD;
  const myColor = inGame ? color : 'white';
  const theirColor = myColor === 'white' ? 'black' : 'white';
  const orientation = flipped ? theirColor : myColor;
  const interactive = phase === 'playing' && turn === color && !state.pending;

  const boardSize = computeBoardSize(area);
  const stackHeight = boardSize + FRAME + 2 * BAR_HEIGHT;
  const isWide = area.width >= WIDE_BREAKPOINT - 48;

  const { captured, balance } = useMemo(() => capturedMaterial(board), [board]);

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

  const players = {
    [myColor]: { name: 'You', detail: inGame ? `Playing ${myColor}` : 'White' },
    [theirColor]: inGame
      ? mode === 'ai'
        ? { name: 'Engine', detail: 'NegaMax · alpha-beta' }
        : { name: 'Opponent', detail: 'Online' }
      : { name: 'Opponent', detail: 'Black' },
  };

  const renderBar = (side) => (
    <PlayerBar
      {...players[side]}
      color={side}
      captured={captured[side[0]]}
      advantage={Math.max(0, side === 'white' ? balance : -balance)}
      active={phase === 'playing' && turn === side}
      thinking={phase === 'playing' && turn === side && side !== color && mode === 'ai'}
    />
  );

  return (
    <div className="app">
      <header className="app-header">
        <div className="d-flex align-items-center px-4 h-100">
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

      <main className="app-main" ref={areaRef}>
        <div className="play-area">
          <section className="board-stack" style={{ width: boardSize + FRAME }} aria-label="Board">
            {renderBar(orientation === 'white' ? 'black' : 'white')}
            <GameBoard
              size={boardSize}
              board={board}
              validMoves={state.validMoves}
              orientation={orientation}
              interactive={interactive}
              lastMove={state.lastMove}
              hint={state.hint}
              result={state.result}
              onMove={makeMove}
            />
            {renderBar(orientation)}
          </section>

          <aside className="side-panel" style={isWide ? { height: stackHeight } : undefined}>
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
                waiting={waiting}
                mode={mode}
                onStart={startGame}
                onCancel={leaveGame}
              />
            )}

            {notice && (
              <div className="notice alert alert-warning small d-flex align-items-center mb-0 py-2" role="alert">
                <span className="me-auto">{notice}</span>
                <button type="button" className="btn-close btn-sm" aria-label="Dismiss" onClick={dismissNotice} />
              </div>
            )}
          </aside>
        </div>
      </main>
    </div>
  );
}
