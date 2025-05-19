import { CommandIcon } from 'lucide-react';

import { Badge } from '@/components/ui/badge';
import { Command } from '@/types/job';

interface CommandItemProps {
  command: Command;
}

const CommandItem = ({ command }: CommandItemProps) => {
  return (
    <div className='flex items-center gap-3 px-5 py-2'>
      <div className='bg-secondary flex h-6 w-6 items-center justify-center rounded-full'>
        <CommandIcon className='text-accent-foreground h-3.5 w-3.5' />
      </div>
      <div className='flex flex-1 items-center justify-between gap-2'>
        <span className='text-xs'>{command.content}</span>
        <Badge variant='outline' className='rounded-full'>
          Order {command.order}
        </Badge>
      </div>
    </div>
  );
};

export default CommandItem;
