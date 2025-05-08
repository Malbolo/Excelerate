import { useState } from 'react';

import { Separator } from '@radix-ui/react-separator';
import { useSearchParams } from 'react-router-dom';

import {
  JobResponse,
  useGetJobDetail,
  useGetJobList,
} from '@/apis/jobManagement';

import AvailableJobList from '../createScheduler/components/AvailableJobList';
import JobPagination from '../createScheduler/components/JobPagination';
import JobSearchInput from '../createScheduler/components/JobSearchInput';
import CommandList from './components/CommandList';

export const ITEMS_PER_PAGE = 6;

const JobManagementPage = () => {
  const [selectedJob, setSelectedJob] = useState<JobResponse | null>(null);
  const getJobDetail = useGetJobDetail();
  const [searchParams] = useSearchParams();
  const currentPage = parseInt(searchParams.get('page') || '1', 10);
  const title = searchParams.get('title') || '';
  const dep = searchParams.get('dep') || '';
  const type = searchParams.get('type') || '';
  const name = searchParams.get('name') || '';

  const { data: jobList } = useGetJobList({
    page: currentPage,
    title,
    dep,
    type,
    name,
    mine: true,
  });

  const { total, jobs } = jobList;

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
            jobs={jobs}
          />
          <JobPagination total={total} />
        </div>
      </main>
      <Separator orientation='vertical' className='mx-2 hidden md:block' />
      {selectedJob ? (
        <CommandList selectedJob={selectedJob} />
      ) : (
        <div className='flex w-[40%] flex-col overflow-hidden bg-gray-100/50 p-8'>
          <p className='text-center text-lg font-bold'>
            Select a job to view details
          </p>
        </div>
      )}
    </div>
  );
};

export default JobManagementPage;
