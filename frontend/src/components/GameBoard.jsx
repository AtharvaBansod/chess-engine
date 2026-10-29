import { memo, useEffect, useMemo, useState } from 'react';
import { Chessboard } from 'react-chessboard';
import { findKing, indexMoves, toPosition } from '../lib/board';

const LIGHT = '#ece4d4';
const DARK = '#b39271';

const styles = {
  lastMove: { backgroundColor: 'rgba(214, 178, 72, 0.42)' },
  selected: { backgroundColor: 'rgba(47, 93, 80, 0.45)' },
  target: {
    background: 'radial-gradient(circle, rgba(31, 42, 55, 0.28) 22%, transparent 24%)',
    cursor: 'pointer',
  },
  capture: {
    background: 'radial-gradient(circle, transparent 62%, rgba(31, 42, 55, 0.3) 64%)',
    cursor: 'pointer',
  },
  mated: { background: 'radial-gradient(circle, rgba(192, 57, 43, 0.85) 0%, rgba(192, 57, 43, 0.25) 70%)' },
};

function GameBoard({ board, validMoves, orientation, interactive, lastMove, hint, result, onMove }) {
  const [selected, setSelected] = useState(null);
  const moveMap = useMemo(() => indexMoves(validMoves), [validMoves]);
  const position = useMemo(() => toPosition(board), [board]);
  const myColour = orientation[0];

  useEffect(() => setSelected(null), [validMoves, interactive]);

  const isLegal = (from, to) => interactive && moveMap.get(from)?.has(to);

  const squareStyles = useMemo(() => {
    const out = {};
    if (lastMove) {
      out[lastMove.from] = styles.lastMove;
      out[lastMove.to] = styles.lastMove;
    }
    if (selected) {
      out[selected] = styles.selected;
      moveMap.get(selected)?.forEach((sq) => {
        out[sq] = { ...out[sq], ...(position[sq] ? styles.capture : styles.target) };
      });
    }
    if (result?.kind === 'checkmate') {
      const king = findKing(board, result.loser[0]);
      if (king) out[king] = styles.mated;
    }
    return out;
  }, [lastMove, selected, moveMap, position, result, board]);

  const arrows = useMemo(() => (hint ? [[hint.from, hint.to, 'rgba(47, 93, 80, 0.8)']] : []), [hint]);

  const handleDrop = (from, to) => {
    if (!isLegal(from, to)) return false;
    onMove(from, to);
    return true;
  };

  const handleSquareClick = (square, piece) => {
    if (!interactive) return;
    if (selected && isLegal(selected, square)) {
      onMove(selected, square);
      return;
    }
    const ownPiece = piece && piece[0] === myColour && moveMap.has(square);
    setSelected(ownPiece && square !== selected ? square : null);
  };

  return (
    <div className="board-frame">
      <Chessboard
        id="main-board"
        position={position}
        boardOrientation={orientation}
        arePiecesDraggable={interactive}
        isDraggablePiece={({ piece }) => interactive && piece[0] === myColour}
        onPieceDragBegin={(_, square) => setSelected(square)}
        onPieceDrop={handleDrop}
        onSquareClick={handleSquareClick}
        onPromotionCheck={() => false}
        customSquareStyles={squareStyles}
        customArrows={arrows}
        areArrowsAllowed={false}
        customLightSquareStyle={{ backgroundColor: LIGHT }}
        customDarkSquareStyle={{ backgroundColor: DARK }}
        customDropSquareStyle={{ boxShadow: 'inset 0 0 0 3px rgba(47, 93, 80, 0.7)' }}
        customBoardStyle={{ borderRadius: '6px', overflow: 'hidden' }}
        animationDuration={180}
      />
    </div>
  );
}

export default memo(GameBoard);
