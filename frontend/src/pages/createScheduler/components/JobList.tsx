import { Check, ChevronRight, TagIcon, UserCircle2Icon } from 'lucide-react';

import { JobManagement } from '@/apis/jobManagement';
import { Badge } from '@/components/ui/badge';
import { Card } from '@/components/ui/card';
import { formatDateTime } from '@/lib/dateFormat';
import { cn } from '@/lib/utils';
import { useLocalDate } from '@/store/useLocalDate';

interface JobListProps {
  selectedJobIds?: Set<string>;
  selectedJobId?: string;
  onJobSelect?: (job: JobManagement, isNowSelected: boolean) => void;
  jobs: JobManagement[];
}

const JobList = ({ selectedJobIds, onJobSelect, selectedJobId, jobs }: JobListProps) => {
  const { locale, place } = useLocalDate();

  const handleJobSelectInternal = (job: JobManagement) => {
    if (onJobSelect) {
      const isCurrentlySelected = selectedJobIds?.has(job.id) || false;
      onJobSelect(job, !isCurrentlySelected);
    }
  };

  return (
    <div className='flex flex-1 flex-col'>
      {jobs.length > 0 ? (
        <div className='grid flex-1 grid-cols-1 content-start gap-2'>
          {jobs.map(job => {
            const isSingleActive = selectedJobId === job.id;

            return (
              <Card
                key={`${job.id}-${job.title}`}
                className={cn(
                  'group flex h-fit cursor-pointer items-start rounded-md border p-3.5 transition-all duration-150 ease-in-out',
                  isSingleActive && 'border-primary/70',
                  selectedJobIds && selectedJobIds.has(job.id) && 'border-primary/70',
                )}
                onClick={() => handleJobSelectInternal(job)}
              >
                <div className='flex w-full flex-1 flex-col justify-between gap-2'>
                  <div className='pb-2'>
                    <span className='flex w-full justify-between pb-1'>
                      <p className='group-hover:text-accent-foreground truncate text-sm font-bold'>{job.title}</p>
                      <Badge variant='outline'>{formatDateTime(job.created_at, locale, place)}</Badge>
                    </span>

                    {job.description && <p className='mt-0.5 line-clamp-2 text-xs text-gray-500'>{job.description}</p>}
                  </div>

                  <div className='flex flex-wrap items-center gap-x-5 gap-y-2 border-t pt-3'>
                    <div className='flex items-center'>
                      <TagIcon className='mr-1.5 h-3.5 w-3.5 flex-shrink-0 text-slate-500' />
                      <span className='inline-block max-w-[120px] truncate rounded bg-slate-100 px-2 py-0.5 text-xs font-medium text-slate-700 ring-1 ring-slate-200/80 ring-inset sm:max-w-[150px]'>
                        {job.type}
                      </span>
                    </div>
                    <div className='flex items-center'>
                      <UserCircle2Icon className='mr-1.5 h-3.5 w-3.5 flex-shrink-0 text-slate-500' />
                      <span className='bg-slate-100 px-2 py-0.5 text-xs font-medium ring-1 ring-slate-200/80 ring-inset sm:max-w-[150px]'>
                        {job.user_name}
                      </span>
                    </div>

                    <Badge
                      variant='secondary'
                      className='ml-auto h-6 w-6 rounded-full p-0 transition-all ease-in-out group-hover:scale-105'
                    >
                      {isSingleActive || (selectedJobIds && selectedJobIds.has(job.id)) ? (
                        <Check className='h-4 w-4' />
                      ) : (
                        <ChevronRight className='h-4 w-4' />
                      )}
                    </Badge>
                  </div>
                </div>
              </Card>
            );
          })}
        </div>
      ) : (
        <div className='flex flex-col items-center justify-center text-center'>
          <p className='text-base font-bold'>No Available Jobs</p>
          <p className='text-sm text-gray-500'>There are currently no jobs to display.</p>
          <p className='text-sm text-gray-500'>New jobs will appear here.</p>
        </div>
      )}
    </div>
  );
};

export default JobList;
