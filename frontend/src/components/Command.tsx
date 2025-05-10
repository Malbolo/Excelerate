import { CSSProperties, useState } from 'react';

import { useSortable } from '@dnd-kit/sortable';
import { CSS } from '@dnd-kit/utilities';
import { Check, MoreVertical } from 'lucide-react';

import { Input } from '@/components/ui/input';
import {
  Popover,
  PopoverContent,
  PopoverTrigger,
} from '@/components/ui/popover';
import { cn } from '@/lib/utils';
import { useJobStore } from '@/store/useJobStore';

interface CommandProps {
  id: string;
  command: string;
  status?: 'pending' | 'processing' | 'success' | 'fail';
  onDelete: (command: string) => void;
  onEdit: (command: string, newCommand: string) => void;
}

const statusColor = {
  pending: 'bg-primary/80',
  processing: 'bg-primary/80',
  success: 'bg-success/80',
  fail: 'bg-destructive/80',
};

const Command: React.FC<CommandProps> = ({
  id,
  command,
  status = 'pending',
  onDelete,
  onEdit,
}) => {
  const [isEditing, setIsEditing] = useState<boolean>(false);
  const [editingCommand, setEdtingCommand] = useState<string>(command);

  const { isEditMode, setIsEditMode } = useJobStore();

  const { attributes, listeners, setNodeRef, transform, transition } =
    useSortable({ id });

  const sortableProps = {
    ref: isEditMode ? undefined : setNodeRef,
    style: isEditMode
      ? {}
      : {
          transform: CSS.Transform.toString(transform),
          transition,
          width: '100%',
          position: 'relative',
        },
    attributes: isEditMode ? {} : attributes,
    listeners: isEditMode ? {} : listeners,
  };

  const handleEditBtnClick = () => {
    if (isEditMode) {
      alert('Edit mode is already on');
      return;
    }
    setIsEditMode(true);
    setIsEditing(true);
  };

  const handleEdit = () => {
    if (!editingCommand.trim()) return;

    onEdit(command, editingCommand);

    setIsEditMode(false);
    setIsEditing(false);
  };

  return (
    <div className='flex items-center justify-between'>
      <div
        ref={sortableProps.ref}
        style={sortableProps.style as CSSProperties}
        {...sortableProps.attributes}
        {...sortableProps.listeners}
        className={cn(
          'group hover:text-accent-foreground flex grow items-center gap-3 rounded-lg px-2 py-1',
          !isEditMode && 'cursor-move',
        )}
      >
        <div
          className={cn(
            statusColor[status],
            'h-1.5 w-1.5 shrink-0 rounded-full transition-all group-hover:scale-125',
          )}
        />
        {isEditing ? (
          <Input
            value={editingCommand}
            onChange={e => setEdtingCommand(e.target.value)}
            onKeyDown={e => e.key === 'Enter' && handleEdit()}
            className='cursor-text'
            onMouseDown={e => {
              e.stopPropagation();
            }}
          />
        ) : (
          <p>{command}</p>
        )}
      </div>

      {isEditing ? (
        <div
          onClick={handleEdit}
          className='bg-primary/80 flex h-6 w-6 cursor-pointer items-center justify-center rounded-full'
        >
          <Check className='h-4 w-4' color='white' />
        </div>
      ) : (
        <Popover>
          <PopoverTrigger>
            <div className='flex h-6 w-6 cursor-pointer items-center justify-center rounded-full border bg-white'>
              <MoreVertical className='h-4 w-4' />
            </div>
          </PopoverTrigger>
          <PopoverContent className='overflow-hidden'>
            <ul className='divide-primary/70 flex w-full flex-col divide-y'>
              <li
                onClick={handleEditBtnClick}
                className='w-full cursor-pointer px-3 py-1 text-center hover:bg-[#F0F7FF]'
              >
                edit
              </li>
              <li
                onClick={() => onDelete(command)}
                className='w-full cursor-pointer px-3 py-1 text-center hover:bg-[#F0F7FF]'
              >
                delete
              </li>
            </ul>
          </PopoverContent>
        </Popover>
      )}
    </div>
  );
};

export default Command;
