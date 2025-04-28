import { Job } from '@/types/scheduler';

import CommandItem from './CommandItem';

interface JobDisplayProps {
  job: Job;
}

const JobDisplay = ({ job }: JobDisplayProps) => {
  return (
    <div className='rounded-lg border border-gray-300 bg-white p-6 shadow'>
      <h2 className='mb-4 text-center text-xl font-semibold text-gray-700'>
        {job.title}
      </h2>
      <div className='space-y-2'>
        {job.commandList.map((command, index) => (
          <CommandItem
            key={command.commandId}
            command={command}
            isFirst={index === 0}
            isLast={index === job.commandList.length - 1}
          />
        ))}
      </div>
    </div>
  );
};

export default JobDisplay;
