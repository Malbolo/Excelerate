import { useLayoutEffect, useRef, useState } from 'react';
import React from 'react';

import { Log, Position } from '@/types/agent';

import Node from './Node';
import RootNode from './RootNode';

interface LLMGraphProps {
  logs: Log[];
  onLogClick?: (log: Log) => void;
  jobName: string;
}

const LLMGraph: React.FC<LLMGraphProps> = ({ logs, onLogClick, jobName }) => {
  const containerRef = useRef<HTMLDivElement>(null);
  const rootNodeRef = useRef<HTMLDivElement>(null);

  const [rootNodePosition, setRootNodePosition] = useState<Position>({
    x: 0,
    y: 0,
  });

  useLayoutEffect(() => {
    if (!rootNodeRef.current || !containerRef.current) return;

    const containerRect = containerRef.current.getBoundingClientRect();

    const rootRect = rootNodeRef.current.getBoundingClientRect();
    setRootNodePosition({
      x: rootRect.left + rootRect.width / 2.0 - containerRect.left + 0.5,
      y: rootRect.bottom - containerRect.top,
    });
  }, []);

  return (
    <section ref={containerRef} className='relative flex flex-col'>
      <RootNode jobName={jobName} ref={rootNodeRef} />

      {logs.length > 0 && (
        <svg className='absolute inset-0 h-full w-full'>
          <line
            x1={rootNodePosition.x}
            y1={rootNodePosition.y}
            x2={rootNodePosition.x}
            y2={10000}
            stroke='#e5e7eb'
            strokeWidth={1}
          />
        </svg>
      )}

      <div className='flex flex-col gap-4'>
        {logs.map(log => (
          <Node
            key={`${log.name}-${log.timestamp}`}
            log={log}
            onLogClick={onLogClick}
          />
        ))}
      </div>
    </section>
  );
};

export default LLMGraph;
