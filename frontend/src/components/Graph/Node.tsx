import { useLayoutEffect, useRef, useState } from 'react';

import { Link } from 'lucide-react';

import { Log, Position } from '@/types/agent';

interface NodeProps {
  log: Log;
  onLogClick?: (log: Log) => void;
}

const Node = ({ log, onLogClick }: NodeProps) => {
  const containerRef = useRef<HTMLDivElement>(null);
  const rootNodeRef = useRef<HTMLDivElement>(null);

  const [rootNodePosition, setRootNodePosition] = useState<Position>({
    x: 0,
    y: 0,
  });

  useLayoutEffect(() => {
    if (!rootNodeRef || !rootNodeRef.current) return;
    if (!containerRef || !containerRef.current) return;

    const containerRect = containerRef.current.getBoundingClientRect();
    const rootRect = rootNodeRef.current.getBoundingClientRect();

    setRootNodePosition({
      x: rootRect.left + rootRect.width / 2.0 - containerRect.left + 0.5,
      y: rootRect.bottom - containerRect.top,
    });
  }, []);

  return (
    <div ref={containerRef} className='ml-4 flex translate-y-3 items-start'>
      <div className='h-5 w-5 translate-y-2 rounded-bl-md border-b border-l border-[#e5e7eb]'></div>
      <div>
        <div className='flex translate-y-3 items-center gap-2'>
          <div
            ref={rootNodeRef}
            className='bg-secondary border-primary/70 z-10 flex h-8 w-8 shrink-0 cursor-pointer items-center justify-center rounded-md border transition-all duration-300 ease-in-out hover:scale-105'
            onClick={() => onLogClick?.(log)}
          >
            <Link className='text-accent-foreground/90 h-4 w-4' />
          </div>
          <p className='text-xs text-gray-600'>{log.name}</p>
        </div>
        {log.subEvents && log.subEvents.length > 0 && (
          <>
            <svg className='pointer-events-none absolute inset-0 h-full w-full'>
              <line
                x1={rootNodePosition.x}
                y1={rootNodePosition.y}
                x2={rootNodePosition.x}
                y2={10000}
                stroke='#e5e7eb'
                strokeWidth={1}
              />
            </svg>

            <div className='flex flex-col gap-4'>
              {log.subEvents.map(subLog => (
                <Node key={`${subLog.name}-${subLog.timestamp}`} log={subLog} onLogClick={onLogClick} />
              ))}
            </div>
          </>
        )}
      </div>
    </div>
  );
};

export default Node;
