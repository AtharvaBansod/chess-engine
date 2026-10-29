import { useLayoutEffect, useRef, useState } from 'react';

export function useElementSize() {
  const ref = useRef(null);
  const [size, setSize] = useState({ width: 0, height: 0 });

  useLayoutEffect(() => {
    const el = ref.current;
    if (!el) return undefined;

    const measure = () => {
      const style = getComputedStyle(el);
      const rect = el.getBoundingClientRect();
      const width = Math.floor(rect.width - parseFloat(style.paddingLeft) - parseFloat(style.paddingRight));
      const height = Math.floor(rect.height - parseFloat(style.paddingTop) - parseFloat(style.paddingBottom));
      setSize((prev) => (prev.width === width && prev.height === height ? prev : { width, height }));
    };

    measure();
    const observer = new ResizeObserver(measure);
    observer.observe(el);
    window.addEventListener('resize', measure);
    document.addEventListener('visibilitychange', measure);
    return () => {
      observer.disconnect();
      window.removeEventListener('resize', measure);
      document.removeEventListener('visibilitychange', measure);
    };
  }, []);

  return [ref, size];
}
