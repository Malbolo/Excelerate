import { useState } from 'react';

import { ChevronDown } from 'lucide-react';

import { Collapsible, CollapsibleTrigger } from '@/components/ui/collapsible';
import { cn } from '@/lib/utils';

import StatusIcon from '../../../components/StatusIcon';

const JobDisplay = ({ status, title }: { status?: string; title: string }) => {
  const [isOpen, setIsOpen] = useState(false);

  return (
    <Collapsible open={isOpen} onOpenChange={setIsOpen} className='w-full'>
      <CollapsibleTrigger className='flex w-full items-center justify-between rounded-lg border p-3 text-left text-lg font-semibold shadow-sm transition-colors'>
        <div className='flex items-center space-x-2'>
          {status && <StatusIcon status={status} />}
          <span>{title}</span>
        </div>
        <ChevronDown
          className={cn('h-5 w-5 transition-transform', isOpen && 'rotate-180')}
        />
      </CollapsibleTrigger>
      {/* <CollapsibleContent className='mt-1 rounded-md border border-gray-200 bg-white p-2 shadow'>
        <div className='space-y-1'>
          {task.commandList.map(command => (
            <CommandItem key={command.commandId} command={command} />
          ))}
        </div>
      </CollapsibleContent> */}
    </Collapsible>
  );
};

export default JobDisplay;
