import { HardDrive } from 'lucide-react';

import { Command } from '@/types/job';

interface CommandItemProps {
  command: Command;
}

const CommandItem = ({ command }: CommandItemProps) => {
  return (
    <div className='flex items-center space-x-2 px-2 py-1.5'>
      <HardDrive className='h-4 w-4 flex-shrink-0 text-gray-400' />
      <span className='text-sm text-gray-700'>{command.content}</span>
    </div>
  );
};

export default CommandItem;
