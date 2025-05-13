import { CheckIcon } from 'lucide-react';

import { JobManagement } from '@/apis/jobManagement';
import { ScrollArea } from '@/components/ui/scroll-area';
import { cn } from '@/lib/utils';

interface AvailableJobListProps {
  selectedJobIds?: Set<string>;
  selectedJob?: JobManagement | null;
  onJobSelect?: (job: JobManagement, checked: boolean) => void;
  jobs: JobManagement[];
}

const AvailableJobList = ({
  selectedJobIds,
  onJobSelect,
  selectedJob,
  jobs,
}: AvailableJobListProps) => {
  const handleJobSelect = async (job: JobManagement, checked: boolean) => {
    onJobSelect && onJobSelect(job, checked);
  };

  return (
    <ScrollArea className='h-0 flex-1 p-2'>
      <div className='space-y-3 p-2'>
        {jobs.length > 0 ? (
          jobs.map(job => (
            <div
              key={`${job.id}-${job.title}`}
              className={cn(
                'flex items-center rounded-md border p-3 transition-colors',
                selectedJob?.id === job.id && 'border-blue-500 bg-blue-100',
              )}
              onClick={() => handleJobSelect(job, true)}
            >
              {selectedJobIds &&
                (selectedJobIds.has(job.id) ? (
                  <div className='flex rounded-full bg-blue-500 p-1'>
                    <CheckIcon className='h-4 w-4 text-white' />
                  </div>
                ) : (
                  <div className='flex rounded-full bg-gray-500 p-1'>
                    <CheckIcon className='h-4 w-4 text-white' />
                  </div>
                ))}
              <div className='flex flex-col space-x-3 overflow-hidden pl-4'>
                <span className='truncate font-medium'>{job.title}</span>
                <span className='text-sm text-gray-500'>
                  {job.description.length > 50
                    ? job.description.substring(0, 50) + '...'
                    : job.description}
                </span>
              </div>
            </div>
          ))
        ) : (
          <div className='py-6 text-center text-gray-500'>
            No available JOBs to display.
          </div>
        )}
      </div>
    </ScrollArea>
  );
};

export default AvailableJobList;
