import { forwardRef, useLayoutEffect, useRef, useState } from 'react';

import { Book, Link } from 'lucide-react';

import { TLog } from '@/types/agent';

export const RootNode = forwardRef<HTMLDivElement, { jobName: string }>(
  ({ jobName }, ref) => {
    return (
      <div className='flex items-center gap-2'>
        <div
          ref={ref}
          className='flex h-8 w-8 items-center justify-center rounded-md bg-[#FFC600]'
        >
          <Book color='white' className='h-4 w-4' />
        </div>
        <p className='text-sm text-gray-500'>{jobName}</p>
      </div>
    );
  },
);

export const Node: React.FC<{ log: TLog }> = ({ log }) => {
  const containerRef = useRef<HTMLDivElement>(null);
  const rootNodeRef = useRef<HTMLDivElement>(null);

  const [rootNodePosition, setRootNodePosition] = useState<{
    x: number;
    y: number;
  }>({ x: 0, y: 0 });

  // Line을 그리기 위해 Node의 위치를 계산
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
      {/* 노드 오른쪽의 가로선 */}
      <div className='h-5 w-5 translate-y-2 rounded-bl-md border-b border-l border-[#AEAEAE]'></div>
      <div>
        <div className='flex translate-y-3 cursor-pointer items-center gap-2'>
          <div
            ref={rootNodeRef}
            className='flex h-8 w-8 items-center justify-center rounded-md bg-[#00A2FF]'
          >
            <Link color='white' className='h-4 w-4' />
          </div>
          <p className='text-sm text-gray-500'>{log.name}</p>
        </div>
        {log.subEvents && log.subEvents.length > 0 && (
          <>
            {/* Node로부터 아래로 뻗어나가는 세로선 */}
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

            {/* 해당 노드의 자식 노드들을 재귀적으로 표시 */}
            <div className='flex flex-col gap-4'>
              {log.subEvents.map(log => (
                <Node key={`${log.name}-${log.timestamp}`} log={log} />
              ))}
            </div>
          </>
        )}
      </div>
    </div>
  );
};
