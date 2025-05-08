import { useState } from 'react';

import { ChevronDown } from 'lucide-react';

import {
  Collapsible,
  CollapsibleContent,
  CollapsibleTrigger,
} from '@/components/ui/collapsible';
import { cn } from '@/lib/utils';
import CommandItem from '@/pages/scheduleDetail/components/CommandItem';
import { Job } from '@/types/scheduler';

import StatusIcon from '../../../components/StatusIcon';
import { getJobStatus } from '../utils/getJobStauts';

interface JobDisplayProps {
  job: Job;
}

const JobDisplay = ({ job }: JobDisplayProps) => {
  const [isOpen, setIsOpen] = useState(false);

  return (
    <Collapsible open={isOpen} onOpenChange={setIsOpen} className='w-full'>
      <CollapsibleTrigger className='flex w-full items-center justify-between rounded-lg border p-3 text-left text-lg font-semibold shadow-sm transition-colors'>
        <div className='flex items-center space-x-2'>
          <StatusIcon status={getJobStatus(job)} />
          <span>{job.title}</span>
        </div>
        <ChevronDown
          className={cn('h-5 w-5 transition-transform', isOpen && 'rotate-180')}
        />
      </CollapsibleTrigger>
      <CollapsibleContent className='mt-1 rounded-md border border-gray-200 bg-white p-2 shadow'>
        <div className='space-y-1'>
          {job.commandList.map(command => (
            <CommandItem key={command.commandId} command={command} />
          ))}
        </div>
      </CollapsibleContent>
    </Collapsible>
  );
};

export default JobDisplay;
