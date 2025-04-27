// src/components/SelectedJobList.tsx (예시 경로)
import { XIcon } from 'lucide-react';

// 타입 임포트
import { Button } from '@/components/ui/button';
import { ScrollArea } from '@/components/ui/scroll-area';
import { Job } from '@/types/scheduler';

interface SelectedJobListProps {
  selectedJobs: Job[];
  onJobDeselect: (jobId: string) => void;
}

const SelectedJobList = ({
  selectedJobs,
  onJobDeselect,
}: SelectedJobListProps) => {
  return (
    <>
      <h2 className='mb-4 text-lg font-semibold'>
        선택된 JOB 목록 ({selectedJobs.length})
      </h2>
      <ScrollArea className='flex-grow rounded-md border p-2'>
        <div className='space-y-2 p-2'>
          {selectedJobs.length > 0 ? (
            selectedJobs.map((job, index) => (
              <div
                key={job.jobId}
                className='flex cursor-grab items-center justify-between rounded-md border bg-white p-3 shadow-sm active:cursor-grabbing'
              >
                <div className='flex items-center space-x-2'>
                  <span className='text-sm font-medium text-gray-500'>
                    {index + 1}.
                  </span>
                  <span className='font-medium'>{job.title}</span>
                </div>
                <Button
                  variant='ghost'
                  size='icon'
                  className='h-7 w-7 text-gray-400 hover:text-red-500'
                  onClick={() => onJobDeselect(job.jobId)}
                  aria-label='선택 해제'
                >
                  <XIcon className='h-4 w-4' />
                </Button>
              </div>
            ))
          ) : (
            <div className='py-6 text-center text-gray-400'>
              왼쪽 목록에서 JOB을 선택하세요.
            </div>
          )}
        </div>
      </ScrollArea>
    </>
  );
};

export default SelectedJobList;
