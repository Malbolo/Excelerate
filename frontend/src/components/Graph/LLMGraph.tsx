import { useLayoutEffect, useRef, useState } from 'react';
import React from 'react';

import { Node, RootNode } from '@/components/Graph/Node';
import { TLog } from '@/types/agent';

interface LLMGraphProps {
  jobName: string;
  logs: TLog[];
  onLogClick: (log: TLog) => void;
}

const LLMGraph: React.FC<LLMGraphProps> = ({ jobName, logs, onLogClick }) => {
  const containerRef = useRef<HTMLDivElement>(null);
  const rootNodeRef = useRef<HTMLDivElement>(null);

  const [rootNodePosition, setRootNodePosition] = useState<{
    x: number;
    y: number;
  }>({ x: 0, y: 0 });

  // Line을 그리기 위해 Root Node의 위치를 계산
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

      {/* Root Node로부터 아래로 뻗어나가는 세로선 */}
      {logs.length > 0 && (
        <svg className='absolute inset-0 h-full w-full'>
          <line
            x1={rootNodePosition.x}
            y1={rootNodePosition.y}
            x2={rootNodePosition.x}
            y2={10000}
            stroke='#AEAEAE'
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
