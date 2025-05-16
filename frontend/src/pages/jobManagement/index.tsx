import { Separator } from '@radix-ui/react-separator';
import { useSearchParams } from 'react-router-dom';

import { JobManagement, useGetJobList } from '@/apis/jobManagement';
import CustomPagination from '@/components/Pagination';

import JobList from '../createScheduler/components/JobList';
import JobSearchInput from '../createScheduler/components/JobSearchInput';
import CommandList from './components/CommandList';

const JobManagementPage = () => {
  const [searchParams, setSearchParams] = useSearchParams();
  const currentPage = parseInt(searchParams.get('page') || '1', 10);
  const selectedJobId = searchParams.get('selectedJob') || '';
  const title = searchParams.get('title') || '';
  const types = searchParams.get('types') || '';
  const name = searchParams.get('name') || '';

  const { data: jobList } = useGetJobList({
    page: currentPage,
    title,
    types,
    name,
    mine: true,
  });

  const { total, jobs } = jobList;

  const handleJobSelect = async (job: JobManagement) => {
    const newSearchParams = new URLSearchParams(searchParams.toString());
    newSearchParams.set('selectedJob', job.id);
    setSearchParams(newSearchParams);
  };

  return (
    <div className='relative container mx-auto flex h-full w-full flex-row'>
      <main className='flex h-full w-[60%] flex-col gap-6 p-8'>
        <header className='flex items-center gap-3 border-b border-gray-200 pb-8'>
          <h1 className='flex-1 text-xl font-bold text-gray-800'>Job Management</h1>
        </header>
        <div className='flex w-full grow flex-col overflow-hidden'>
          <JobSearchInput />
          <JobList selectedJobId={selectedJobId} onJobSelect={handleJobSelect} jobs={jobs} />
          <CustomPagination totalPages={total} />
        </div>
      </main>
      <Separator orientation='vertical' className='mx-2 hidden md:block' />
      {selectedJobId ? (
        <CommandList selectedJobId={selectedJobId} />
      ) : (
        <div className='flex w-[40%] flex-col overflow-hidden bg-gray-100/50 p-8'>
          <p className='text-center text-lg font-bold'>Select a job to view details</p>
        </div>
      )}
    </div>
  );
};

export default JobManagementPage;
