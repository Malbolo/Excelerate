import { useState } from 'react';

import CheckIcon from '../assets/icons/checkIcon.svg?react';
import MoreMenuIcon from '../assets/icons/moreMenuIcon.svg?react';
import { cn } from '../lib/utils';
import { Input } from './ui/input';
import { Popover, PopoverContent, PopoverTrigger } from './ui/popover';

interface CommandProps {
  command: string;
  status?: 'pending' | 'processing' | 'success' | 'fail';
  onDelete?: () => void;
  onEdit?: (command: string, newCommand: string) => void;
}

const statusColor = {
  pending: 'bg-disabled',
  processing: 'bg-processing',
  success: 'bg-success',
  fail: 'bg-fail',
};

const Command: React.FC<CommandProps> = ({
  command,
  status = 'pending',
  onDelete,
  onEdit,
}) => {
  const [isEditing, setIsEditing] = useState<boolean>(false);
  const [editingCommand, setEdtingCommand] = useState<string>(command);

  const handleEdit = () => {
    if (!editingCommand.trim()) return;

    if (onEdit) {
      onEdit(command, editingCommand);
    }
    setIsEditing(false);
  };

  return (
    <div className='flex items-center justify-between'>
      <div className='flex grow items-center gap-2 pr-2'>
        <div
          className={cn(statusColor[status], 'h-4 w-4 shrink-0 rounded-full')}
        ></div>
        {isEditing ? (
          <Input
            value={editingCommand}
            onChange={e => setEdtingCommand(e.target.value)}
            onKeyDown={e => e.key === 'Enter' && handleEdit()}
            className=''
          />
        ) : (
          <p>{command}</p>
        )}
      </div>

      {isEditing ? (
        <div
          onClick={handleEdit}
          className='bg-success flex h-6 w-6 cursor-pointer items-center justify-center rounded-full'
        >
          <CheckIcon />
        </div>
      ) : (
        <Popover>
          <PopoverTrigger>
            <div className='border-border flex h-6 w-6 cursor-pointer items-center justify-center rounded-full border bg-white'>
              <MoreMenuIcon />
            </div>
          </PopoverTrigger>
          <PopoverContent className='overflow-hidden'>
            <ul className='flex w-full flex-col divide-y'>
              <li
                onClick={() => setIsEditing(true)}
                className='w-full cursor-pointer px-3 py-1 text-center hover:bg-black/10'
              >
                수정
              </li>
              <li
                onClick={onDelete}
                className='w-full cursor-pointer px-3 py-1 text-center hover:bg-black/10'
              >
                삭제
              </li>
            </ul>
          </PopoverContent>
        </Popover>
      )}
    </div>
  );
};

export default Command;
