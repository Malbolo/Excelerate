import { useState } from 'react';

import { Separator } from '@radix-ui/react-separator';

import { JobResponse, useGetJobDetail } from '@/apis/jobManagement';
import { Button } from '@/components/ui/button';

import AvailableJobList from '../createScheduler/components/AvailableJobList';
import JobPagination from '../createScheduler/components/JobPagination';
import JobSearchInput from '../createScheduler/components/JobSearchInput';
import CommandItem from './components/CommandItem';

export const ITEMS_PER_PAGE = 6;

const JobManagementPage = () => {
  const [selectedJob, setSelectedJob] = useState<JobResponse | null>(null);

  const getJobDetail = useGetJobDetail();

  const handleJobSelect = async (job: JobResponse) => {
    const jobDetail = await getJobDetail(job.id);
    setSelectedJob(jobDetail);
  };

  return (
    <div className='relative container mx-auto flex h-full w-full flex-row'>
      <main className='flex h-full w-[60%] flex-col gap-6 p-8'>
        <header className='flex items-center gap-3 border-b border-gray-200 pb-8'>
          <h1 className='flex-1 text-xl font-bold text-gray-800'>
            Job Management
          </h1>
        </header>
        <div className='flex w-full grow flex-col overflow-hidden'>
          <JobSearchInput />
          <AvailableJobList
            onJobSelect={handleJobSelect}
            selectedJob={selectedJob}
          />
          <JobPagination />
        </div>
      </main>
      <Separator orientation='vertical' className='mx-2 hidden md:block' />
      <div className='flex w-[40%] flex-col overflow-hidden bg-gray-100/50 p-8'>
        <section className='flex grow flex-col gap-2'>
          <div className='flex items-center justify-between gap-2'>
            <p className='text-lg font-bold'>{selectedJob?.title}</p>
          </div>
          <div className='mt-4 flex flex-col gap-2'>
            {selectedJob?.commands.map(command => (
              <CommandItem
                key={`${command.content}-${command.order}`}
                commandTitle={command.content}
              />
            ))}
          </div>
        </section>
        <div className='flex items-center justify-center gap-4'>
          <Button variant='destructive' className='h-12 w-1/2 p-4'>
            delete
          </Button>
          <Button variant='default' className='h-12 w-1/2 p-4'>
            edit
          </Button>
        </div>
      </div>
    </div>
  );
};

export default JobManagementPage;
