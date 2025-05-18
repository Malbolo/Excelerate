import { useSortable } from '@dnd-kit/sortable';
import { CSS } from '@dnd-kit/utilities';
import { GripVertical } from 'lucide-react';
import { X } from 'lucide-react';

import { JobManagement } from '@/apis/jobManagement';
import { Button } from '@/components/ui/button';
import { cn } from '@/lib/utils';

interface SortableJobItemProps {
  job: JobManagement;
  index: number;
  onJobDeselect: (jobId: string) => void;
}

const SortableJobItem = ({ job, index, onJobDeselect }: SortableJobItemProps) => {
  const { attributes, listeners, setNodeRef, transform, transition, isDragging } = useSortable({ id: job.id });

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
      className={cn(
        'group bg-card flex items-center gap-3 rounded-lg border p-3',
        'hover:border-primary/70 hover:box-shadow',
        isDragging && 'border-primary/70 hover:box-shadow',
      )}
    >
      <button
        {...listeners}
        aria-label='Drag to change order'
        className={cn('flex h-7 w-7 cursor-pointer items-center justify-center rounded-md', 'transition-colors')}
      >
        <GripVertical className='h-3 w-3' />
      </button>

      <div className='flex min-w-0 flex-1 items-center gap-3'>
        <div className='bg-secondary text-accent-foreground flex h-6 w-6 items-center justify-center rounded-full text-xs'>
          {index + 1}
        </div>
        <span className='text-foreground truncate font-medium'>{job.title}</span>
      </div>

      <Button
        variant='ghost'
        size='icon'
        className={cn(
          'h-7 w-7 opacity-0 transition-opacity group-hover:opacity-100',
          'hover:bg-destructive/10 hover:text-destructive transition-colors',
        )}
        onClick={() => onJobDeselect(job.id)}
        aria-label='Remove job'
      >
        <X className='h-4 w-4' />
      </Button>
    </div>
  );
};

export default SortableJobItem;
