import { CheckCircle2, Circle, TagIcon, UserCircle2Icon } from 'lucide-react';

import { JobManagement } from '@/apis/jobManagement';
import { ScrollArea } from '@/components/ui/scroll-area';
import { cn } from '@/lib/utils';

interface AvailableJobListProps {
  selectedJobIds?: Set<string>;
  selectedJobId?: string;
  onJobSelect?: (job: JobManagement, isNowSelected: boolean) => void;
  jobs: JobManagement[];
}

const AvailableJobList = ({
  selectedJobIds,
  onJobSelect,
  selectedJobId,
  jobs,
}: AvailableJobListProps) => {
  const handleJobSelectInternal = (job: JobManagement) => {
    if (onJobSelect) {
      const isCurrentlySelected = selectedJobIds?.has(job.id) || false;
      onJobSelect(job, !isCurrentlySelected);
    }
  };

  return (
    <ScrollArea className='h-0 flex-1'>
      <div className='space-y-2.5 p-3'>
        {jobs.length > 0 ? (
          jobs.map(job => {
            const isMultiSelected = selectedJobIds?.has(job.id) || false;
            const isSingleActive = selectedJobId === job.id;

            return (
              <div
                key={`${job.id}-${job.title}`}
                className={cn(
                  'group flex cursor-pointer items-start space-x-3 rounded-md border bg-white p-3.5 shadow-sm transition-all duration-150 ease-in-out hover:border-blue-400 hover:shadow-md',
                  isSingleActive &&
                    'border-blue-600 ring-2 ring-blue-500 ring-offset-1',
                  isMultiSelected &&
                    !isSingleActive &&
                    'border-sky-500 bg-sky-50',
                  isMultiSelected &&
                    isSingleActive &&
                    'border-blue-600 bg-sky-50 ring-2 ring-blue-500 ring-offset-1',
                )}
                onClick={() => handleJobSelectInternal(job)}
              >
                {selectedJobIds && (
                  <div className='pt-0.5'>
                    {isMultiSelected ? (
                      <CheckCircle2 className='h-5 w-5 text-blue-600' />
                    ) : (
                      <Circle className='h-5 w-5 text-gray-300 transition-colors group-hover:text-gray-400' />
                    )}
                  </div>
                )}

                {!selectedJobIds && selectedJobId && (
                  <div className='pt-0.5'>
                    {isSingleActive ? (
                      <CheckCircle2 className='h-5 w-5 text-blue-600' />
                    ) : (
                      <Circle className='h-5 w-5 text-gray-300 transition-colors group-hover:text-gray-400' />
                    )}
                  </div>
                )}

                <div className='flex-1 overflow-hidden'>
                  <span className='block truncate text-sm font-semibold text-gray-800 group-hover:text-blue-700'>
                    {job.title}
                  </span>

                  {job.description && (
                    <p className='mt-0.5 line-clamp-2 text-xs text-gray-500'>
                      {job.description}
                    </p>
                  )}

                  <div className='mt-2.5 flex flex-wrap items-center gap-x-5 gap-y-2 border-t border-gray-200 pt-2.5'>
                    <div className='flex items-center'>
                      <TagIcon className='mr-1.5 h-3.5 w-3.5 flex-shrink-0 text-slate-500' />
                      <span className='inline-block max-w-[120px] truncate rounded bg-slate-100 px-2 py-0.5 text-xs font-medium text-slate-700 ring-1 ring-slate-200/80 ring-inset sm:max-w-[150px]'>
                        {job.type}
                      </span>
                    </div>
                    <div className='flex items-center'>
                      <UserCircle2Icon className='mr-1.5 h-3.5 w-3.5 flex-shrink-0 text-slate-500' />
                      <span className='bg-slate-100 px-2 py-0.5 text-xs font-medium text-gray-700 text-slate-700 ring-1 ring-slate-200/80 ring-inset sm:max-w-[150px]'>
                        {job.user_name}
                      </span>
                    </div>
                  </div>
                </div>
              </div>
            );
          })
        ) : (
          <div className='flex flex-col items-center justify-center py-12 text-center'>
            <p className='text-base font-semibold text-gray-700'>
              No Available Jobs
            </p>
            <p className='mt-1 text-sm text-gray-500'>
              There are currently no jobs to display. New jobs will appear here.
            </p>
          </div>
        )}
      </div>
    </ScrollArea>
  );
};

export default AvailableJobList;
