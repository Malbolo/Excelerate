import { useCallback } from 'react';

import {
  DndContext,
  DragEndEvent,
  KeyboardSensor,
  PointerSensor,
  closestCenter,
  useSensor,
  useSensors,
} from '@dnd-kit/core';
import {
  SortableContext,
  arrayMove,
  sortableKeyboardCoordinates,
  verticalListSortingStrategy,
} from '@dnd-kit/sortable';
import { MousePointerClick } from 'lucide-react';

import { JobManagement } from '@/apis/jobManagement';
import { ScrollArea } from '@/components/ui/scroll-area';

import SortableJobItem from './SortableJobItem';

interface SelectedJobListProps {
  selectedJobs: JobManagement[];
  handleJobOrderChange: (newOrder: JobManagement[]) => void;
  handleJobDeselect: (jobId: string) => void;
}

const SelectedJobList = ({ selectedJobs, handleJobOrderChange, handleJobDeselect }: SelectedJobListProps) => {
  const sensors = useSensors(
    useSensor(PointerSensor),
    useSensor(KeyboardSensor, {
      coordinateGetter: sortableKeyboardCoordinates,
    }),
  );

  const onDragEnd = (event: DragEndEvent) => {
    const { active, over } = event;

    if (over && active.id !== over.id) {
      const oldIndex = selectedJobs.findIndex(job => job.id === active.id);
      const newIndex = selectedJobs.findIndex(job => job.id === over.id);

      const newOrder = arrayMove(selectedJobs, oldIndex, newIndex);
      handleJobOrderChange(newOrder);
    }
  };

  const jobIds = selectedJobs.map(job => job.id);

  const onJobDeselect = useCallback((jobId: string) => {
    handleJobDeselect(jobId);
  }, []);

  return (
    <div className='flex h-full flex-col'>
      {selectedJobs.length > 0 ? (
        <ScrollArea className='flex-1'>
          <DndContext sensors={sensors} collisionDetection={closestCenter} onDragEnd={onDragEnd}>
            <SortableContext items={jobIds} strategy={verticalListSortingStrategy}>
              <div className='space-y-2 p-2'>
                {selectedJobs.map((job, index) => (
                  <SortableJobItem key={job.id} job={job} index={index} onJobDeselect={onJobDeselect} />
                ))}
              </div>
            </SortableContext>
          </DndContext>
        </ScrollArea>
      ) : (
        <div className='flex flex-1 items-center justify-center'>
          <div className='animate-scale flex flex-col items-center gap-2'>
            <MousePointerClick size={20} className='text-accent-foreground' />
            <p className='text-sm'>Choose jobs to include in your schedule.</p>
          </div>
        </div>
      )}
    </div>
  );
};

export default SelectedJobList;
