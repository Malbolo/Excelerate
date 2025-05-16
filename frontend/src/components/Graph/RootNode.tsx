import { forwardRef } from 'react';

import { Book } from 'lucide-react';

interface RootNodeProps {
  jobName: string;
}

const RootNode = forwardRef<HTMLDivElement, RootNodeProps>(({ jobName }, ref) => {
  return (
    <div className='flex items-center gap-2'>
      <div ref={ref} className='bg-primary z-10 flex h-8 w-8 items-center justify-center rounded-md'>
        <Book color='white' className='h-4 w-4' />
      </div>
      <p className='text-xs text-gray-600'>{jobName}</p>
    </div>
  );
});

export default RootNode;
