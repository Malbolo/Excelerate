import { useState } from 'react';

import { Book, ChevronDown } from 'lucide-react';

import { Job } from '@/apis/jobManagement';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Collapsible, CollapsibleContent, CollapsibleTrigger } from '@/components/ui/collapsible';
import { cn } from '@/lib/utils';
import { Status } from '@/types/job';

import CommandItem from './CommandItem';
import StatusIcon from './StatusIcon';

interface JobDisplayProps {
  status?: Status;
  title: string;
  job: Job;
}

const JobDisplay = ({ status, title, job }: JobDisplayProps) => {
  const [isOpen, setIsOpen] = useState(false);

  return (
    <Collapsible open={isOpen} onOpenChange={setIsOpen} className='card-gradient w-full rounded-lg border'>
      <CollapsibleTrigger className='flex w-full cursor-pointer items-center justify-between px-4 py-3 text-left'>
        <div className='flex items-center gap-3'>
          <div className='bg-secondary flex h-6 w-6 items-center justify-center rounded-full'>
            <Book className='text-accent-foreground h-3.5 w-3.5' />
          </div>

          <div className='flex items-center gap-3 overflow-hidden'>
            <span className='truncate text-sm'>{title}</span>
            {status && <StatusIcon status={status} />}
          </div>
        </div>

        <div className='flex items-center gap-2'>
          <Badge variant='secondary' className='rounded-full px-2 py-0.5 text-xs'>
            {job.commands.length} commands
          </Badge>

          <Button
            variant='ghost'
            size='icon'
            className={cn(
              'flex h-7 w-7 items-center justify-center transition-transform duration-200',
              isOpen ? 'rotate-180' : 'bg-transparent',
            )}
          >
            <ChevronDown className='text-accent-foreground h-4 w-4' />
          </Button>
        </div>
      </CollapsibleTrigger>

      <CollapsibleContent>
        <div className='border-t px-4 py-2'>
          <div className='space-y-1'>
            {job.commands.length > 0 ? (
              job.commands.map((command, index) => (
                <div
                  key={`${job.id}-${command.order}`}
                  className={cn('rounded-md', index !== job.commands.length - 1 && 'mb-1')}
                >
                  <CommandItem command={command} />
                </div>
              ))
            ) : (
              <div className='py-3 text-center text-sm text-gray-500'>No commands defined.</div>
            )}
          </div>
        </div>
      </CollapsibleContent>
    </Collapsible>
  );
};

export default JobDisplay;
