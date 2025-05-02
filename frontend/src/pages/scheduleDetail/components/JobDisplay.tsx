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

// todo: 더미데이터이기에 실제 변경 예정
const JobDisplay = ({ job }: JobDisplayProps) => {
  const [isOpen, setIsOpen] = useState(false);

  const getStatusStyles = () => {
    switch (getJobStatus(job)) {
      case 'success':
        return 'bg-green-50 hover:bg-green-100 border-green-200';
      case 'error':
        return 'bg-red-50 hover:bg-red-100 border-red-200 text-red-800';
      default:
        return 'bg-gray-50 hover:bg-gray-100 border-gray-200';
    }
  };

  return (
    <Collapsible open={isOpen} onOpenChange={setIsOpen} className='w-full'>
      <CollapsibleTrigger
        className={cn(
          'flex w-full items-center justify-between rounded-lg border p-3 text-left text-lg font-semibold shadow-sm transition-colors',
          getStatusStyles(),
        )}
      >
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
          {job.commandList.map((command, index) => (
            <CommandItem
              key={command.commandId}
              command={command}
              isFirst={index === 0}
              isLast={index === job.commandList.length - 1}
            />
          ))}
        </div>
      </CollapsibleContent>
    </Collapsible>
  );
};

export default JobDisplay;
