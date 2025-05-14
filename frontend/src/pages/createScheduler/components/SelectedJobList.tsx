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

import { JobManagement } from '@/apis/jobManagement';
import { ScrollArea } from '@/components/ui/scroll-area';

import SortableJobItem from './SortableJobItem';

interface SelectedJobListProps {
  selectedJobs: JobManagement[];
  handleJobOrderChange: (newOrder: JobManagement[]) => void;
  handleJobDeselect: (jobId: string) => void;
}

const SelectedJobList = ({
  selectedJobs,
  handleJobOrderChange,
  handleJobDeselect,
}: SelectedJobListProps) => {
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
    <>
      <h2 className='mb-4 text-lg font-semibold'>
        Selected JOB List ({selectedJobs.length})
      </h2>
      <ScrollArea className='h-0 flex-1 rounded-md border p-2'>
        <DndContext
          sensors={sensors}
          collisionDetection={closestCenter}
          onDragEnd={onDragEnd}
        >
          <SortableContext
            items={jobIds}
            strategy={verticalListSortingStrategy}
          >
            <div className='space-y-2 p-2'>
              {selectedJobs.length > 0 ? (
                selectedJobs.map((job, index) => (
                  <SortableJobItem
                    key={job.id}
                    job={job}
                    index={index}
                    onJobDeselect={onJobDeselect}
                  />
                ))
              ) : (
                <div className='py-6 text-center text-gray-400'>
                  Select JOBs from the left list.
                </div>
              )}
            </div>
          </SortableContext>
        </DndContext>
      </ScrollArea>
    </>
  );
};

export default SelectedJobList;
