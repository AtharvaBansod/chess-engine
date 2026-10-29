import { useEffect, useRef } from 'react';

export default function MoveList({ moves }) {
  const scroller = useRef(null);

  useEffect(() => {
    const el = scroller.current;
    if (el) el.scrollTop = el.scrollHeight;
  }, [moves.length]);

  const rows = [];
  for (let i = 0; i < moves.length; i += 2) rows.push([moves[i], moves[i + 1]]);

  return (
    <div className="move-list" ref={scroller}>
      {rows.length === 0 ? (
        <p className="text-secondary small mb-0 px-3 py-3">No moves yet.</p>
      ) : (
        <table className="table table-sm mb-0">
          <tbody>
            {rows.map(([white, black], i) => (
              <tr key={i}>
                <td className="move-no">{i + 1}.</td>
                <td className={!black && moves.length % 2 === 1 ? 'latest' : ''}>{white}</td>
                <td className={black && i === rows.length - 1 ? 'latest' : ''}>{black}</td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </div>
  );
}
