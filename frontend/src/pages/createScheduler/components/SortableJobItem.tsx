import { useSortable } from '@dnd-kit/sortable';
import { CSS } from '@dnd-kit/utilities';
import { XIcon } from 'lucide-react';

import { Button } from '@/components/ui/button';
import { Job } from '@/types/scheduler';

interface SortableJobItemProps {
  job: Job;
  index: number;
  onJobDeselect: (jobId: string) => void;
}

const SortableJobItem = ({
  job,
  index,
  onJobDeselect,
}: SortableJobItemProps) => {
  const {
    attributes,
    listeners,
    setNodeRef,
    transform,
    transition,
    isDragging,
  } = useSortable({ id: job.jobId });

  const style = {
    transform: CSS.Transform.toString(transform),
    transition,
    opacity: isDragging ? 0.5 : 1,
    zIndex: isDragging ? 10 : 'auto',
    boxShadow: isDragging ? '0 2px 10px rgba(0,0,0,0.1)' : 'none',
  };

  return (
    <div
      ref={setNodeRef}
      style={style}
      {...attributes}
      className='flex touch-none items-center justify-between rounded-md border bg-white p-3 shadow-sm'
    >
      <div className='flex flex-grow items-center space-x-2 overflow-hidden'>
        <button
          {...listeners}
          aria-label='Drag to change order'
          className='-ml-1 cursor-grab touch-none p-1 active:cursor-grabbing'
        >
          <svg
            width='15'
            height='15'
            viewBox='0 0 15 15'
            fill='none'
            xmlns='http://www.w3.org/2000/svg'
          >
            <path
              d='M5.5 4.5C5.5 4.77614 5.27614 5 5 5C4.72386 5 4.5 4.77614 4.5 4.5C4.5 4.22386 4.72386 4 5 4C5.27614 4 5.5 4.22386 5.5 4.5ZM10.5 4.5C10.5 4.77614 10.2761 5 10 5C9.72386 5 9.5 4.77614 9.5 4.5C9.5 4.22386 9.72386 4 10 4C10.2761 4 10.5 4.22386 10.5 4.5ZM5.5 7.5C5.5 7.77614 5.27614 8 5 8C4.72386 8 4.5 7.77614 4.5 7.5C4.5 7.22386 4.72386 7 5 7C5.27614 7 5.5 7.22386 5.5 7.5ZM10.5 7.5C10.5 7.77614 10.2761 8 10 8C9.72386 8 9.5 7.77614 9.5 7.5C9.5 7.22386 9.72386 7 10 7C10.2761 7 10.5 7.22386 10.5 7.5ZM5.5 10.5C5.5 10.7761 5.27614 11 5 11C4.72386 11 4.5 10.7761 4.5 10.5C4.5 10.2239 4.72386 10 5 10C5.27614 10 5.5 10.2239 5.5 10.5ZM10.5 10.5C10.5 10.7761 10.2761 11 10 11C9.72386 11 9.5 10.7761 9.5 10.5C9.5 10.2239 9.72386 10 10 10C10.2761 10 10.5 10.2239 10.5 10.5Z'
              fill='currentColor'
              fillRule='evenodd'
              clipRule='evenodd'
            ></path>
          </svg>
        </button>
        <span className='text-sm font-medium text-gray-500'>{index + 1}.</span>
        <span className='truncate font-medium'>{job.title}</span>{' '}
      </div>
      <Button
        variant='ghost'
        size='icon'
        className='ml-2 h-7 w-7 flex-shrink-0 text-gray-400 hover:text-red-500' // flex-shrink-0 추가
        onClick={() => onJobDeselect(job.jobId)}
        aria-label='Deselect'
      >
        <XIcon className='h-4 w-4' />
      </Button>
    </div>
  );
};

export default SortableJobItem;
