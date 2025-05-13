import { forwardRef } from 'react';

import { Book } from 'lucide-react';

interface RootNodeProps {
  jobName: string;
}

const RootNode = forwardRef<HTMLDivElement, RootNodeProps>(
  ({ jobName }, ref) => {
    return (
      <div className='flex items-center gap-2'>
        <div
          ref={ref}
          className='flex h-8 w-8 items-center justify-center rounded-md bg-[#FFC600]'
        >
          <Book color='white' className='h-4 w-4' />
        </div>
        <p className='text-sm text-gray-500'>{jobName}</p>
      </div>
    );
  },
);

export default RootNode;
