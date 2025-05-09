import { Dispatch, SetStateAction } from 'react';

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

import Command from '@/components/Command';
import { useJobStore } from '@/store/useJobStore';
import { TCommand } from '@/types/job';

interface CommandListProps {
  commandList: TCommand[];
  setCommandList: Dispatch<SetStateAction<TCommand[]>>;
}

const CommandList: React.FC<CommandListProps> = ({
  commandList,
  setCommandList,
}) => {
  const { setCanSaveJob } = useJobStore();

  const sensors = useSensors(
    useSensor(PointerSensor),
    useSensor(KeyboardSensor, {
      coordinateGetter: sortableKeyboardCoordinates,
    }),
  );

  const handleEditCommand = (command: string, newCommand: string) => {
    setCommandList(prev =>
      prev.map(cmd =>
        cmd.title === command
          ? { status: 'pending', title: newCommand }
          : { status: 'pending', title: cmd.title },
      ),
    );

    setCanSaveJob(false);
  };

  const handleDeleteCommand = (command: string) => {
    setCommandList(prev =>
      prev
        .filter(prevCommand => prevCommand.title !== command)
        .map(cmd => ({ ...cmd, status: 'pending' })),
    );

    setCanSaveJob(false);
  };

  const handleDragEnd = (event: DragEndEvent) => {
    const { active, over } = event;

    if (over && active.id !== over.id) {
      setCommandList(items => {
        const oldIndex = items.findIndex(item => item.title === active.id);
        const newIndex = items.findIndex(item => item.title === over.id);

        return arrayMove(items, oldIndex, newIndex).map(item => ({
          ...item,
          status: 'pending',
        }));
      });
    }

    setCanSaveJob(false);
  };

  return (
    <div className='flex flex-col gap-2 overflow-y-auto'>
      <DndContext
        sensors={sensors}
        collisionDetection={closestCenter}
        onDragEnd={handleDragEnd}
      >
        <SortableContext
          items={commandList.map(cmd => cmd.title)}
          strategy={verticalListSortingStrategy}
        >
          {commandList.map((command, index) => (
            <Command
              key={`${command.title}-${index}`}
              id={`${command.title}-${index}`}
              command={command.title}
              status={command.status}
              onDelete={handleDeleteCommand}
              onEdit={handleEditCommand}
            />
          ))}
        </SortableContext>
      </DndContext>
    </div>
  );
};

export default CommandList;
