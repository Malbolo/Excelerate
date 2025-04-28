import { Checkbox } from '@/components/ui/checkbox';
import { ScrollArea } from '@/components/ui/scroll-area';
import { Job } from '@/types/scheduler';

interface AvailableJobListProps {
  jobs: Job[];
  selectedJobIds: Set<string>;
  onJobSelect: (job: Job, checked: boolean) => void;
}

const AvailableJobList = ({
  jobs,
  selectedJobIds,
  onJobSelect,
}: AvailableJobListProps) => {
  return (
    <ScrollArea className='h-0 flex-1 rounded-md border p-2'>
      <div className='space-y-3 p-2'>
        {jobs.length > 0 ? (
          jobs.map(job => (
            <div
              key={job.jobId}
              className='flex items-center justify-between rounded-md border p-3 transition-colors hover:bg-gray-50'
            >
              <div className='flex items-center space-x-3 overflow-hidden'>
                <Checkbox
                  id={`avail-${job.jobId}`}
                  checked={selectedJobIds.has(job.jobId)}
                  onCheckedChange={checked => onJobSelect(job, !!checked)}
                />
                <label
                  htmlFor={`avail-${job.jobId}`}
                  className='flex cursor-pointer flex-col'
                >
                  <span className='truncate font-medium'>{job.title}</span>
                  <span className='text-sm text-gray-500'>
                    {job.description.length > 50
                      ? job.description.substring(0, 50) + '...'
                      : job.description}
                  </span>
                </label>
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
