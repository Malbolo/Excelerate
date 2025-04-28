import { useMemo } from 'react';

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

import { ScrollArea } from '@/components/ui/scroll-area';
import { Job } from '@/types/scheduler';

import SortableJobItem from './SortableJobItem';

interface SelectedJobListProps {
  selectedJobs: Job[];
  onJobDeselect: (jobId: string) => void;
  onOrderChange: (newOrder: Job[]) => void;
}

export function SelectedJobList({
  selectedJobs,
  onJobDeselect,
  onOrderChange,
}: SelectedJobListProps) {
  const sensors = useSensors(
    useSensor(PointerSensor),
    useSensor(KeyboardSensor, {
      coordinateGetter: sortableKeyboardCoordinates,
    }),
  );

  const handleDragEnd = (event: DragEndEvent) => {
    const { active, over } = event;

    if (over && active.id !== over.id) {
      const oldIndex = selectedJobs.findIndex(job => job.jobId === active.id);
      const newIndex = selectedJobs.findIndex(job => job.jobId === over.id);

      const newOrder = arrayMove(selectedJobs, oldIndex, newIndex);
      onOrderChange(newOrder);
    }
  };

  const jobIds = useMemo(
    () => selectedJobs.map(job => job.jobId),
    [selectedJobs],
  );

  return (
    <>
      <h2 className='mb-4 text-lg font-semibold'>
        선택된 JOB 목록 ({selectedJobs.length})
      </h2>
      <ScrollArea className='h-0 flex-1 rounded-md border p-2'>
        <DndContext
          sensors={sensors}
          collisionDetection={closestCenter}
          onDragEnd={handleDragEnd}
        >
          <SortableContext
            items={jobIds}
            strategy={verticalListSortingStrategy}
          >
            <div className='space-y-2 p-2'>
              {selectedJobs.length > 0 ? (
                selectedJobs.map((job, index) => (
                  <SortableJobItem
                    key={job.jobId}
                    job={job}
                    index={index}
                    onJobDeselect={onJobDeselect}
                  />
                ))
              ) : (
                <div className='py-6 text-center text-gray-400'>
                  왼쪽 목록에서 JOB을 선택하세요.
                </div>
              )}
            </div>
          </SortableContext>
        </DndContext>
      </ScrollArea>
    </>
  );
}
