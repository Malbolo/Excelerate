import { useCallback, useMemo, useState } from 'react';

import { Separator } from '@radix-ui/react-separator';
import { useSearchParams } from 'react-router-dom';

import { Job } from '@/types/scheduler';

import AvailableJobList from '../createScheduler/components/AvailableJobList';
import JobPagination from '../createScheduler/components/JobPagination';
import JobSearchInput from '../createScheduler/components/JobSearchInput';
import { allDummyJobs } from '../createScheduler/data';

const ITEMS_PER_PAGE = 6;

const JobManagementPage = () => {
  const [searchParams, setSearchParams] = useSearchParams();

  const keyword = searchParams.get('keyword') || '';
  const currentPage = parseInt(searchParams.get('page') || '1', 10);

  const [selectedJob, setSelectedJob] = useState<Job | null>(null);

  const handleJobSelect = (job: Job) => {
    setSelectedJob(job);
  };

  const handleSearch = (newKeyword: string) => {
    setSearchParams(
      prev => {
        prev.set('keyword', newKeyword);
        prev.set('page', '1');
        return prev;
      },
      { replace: true },
    );
  };

  const filteredJobs = useMemo(() => {
    if (!keyword) return allDummyJobs;
    const lowerCaseKeyword = keyword.toLowerCase();
    return allDummyJobs.filter(
      job =>
        job.title.toLowerCase().includes(lowerCaseKeyword) ||
        job.description.toLowerCase().includes(lowerCaseKeyword),
    );
  }, [keyword]);

  const { paginatedJobs, totalPages } = useMemo(() => {
    const total = Math.ceil(filteredJobs.length / ITEMS_PER_PAGE);
    const adjustedPage = Math.min(currentPage, total > 0 ? total : 1);
    const startIndex = (adjustedPage - 1) * ITEMS_PER_PAGE;
    const endIndex = startIndex + ITEMS_PER_PAGE;
    const jobs = filteredJobs.slice(startIndex, endIndex);
    return { paginatedJobs: jobs, totalPages: total };
  }, [filteredJobs, currentPage]);

  const handlePageChange = useCallback(
    (page: number) => {
      if (page >= 1 && page <= totalPages) {
        setSearchParams(
          prev => {
            prev.set('page', page.toString());
            return prev;
          },
          { replace: true },
        );
      }
    },
    [totalPages, setSearchParams],
  );

  return (
    <div className='relative container mx-auto flex h-full w-full flex-row'>
      <main className='flex h-full w-[60%] flex-col gap-6'>
        <header className='flex items-center gap-3 border-b border-gray-200 pb-8'>
          <h1 className='flex-1 text-xl font-bold text-gray-800'>
            Job Management
          </h1>
        </header>
        <div className='flex w-full grow flex-col overflow-hidden'>
          <JobSearchInput initialKeyword={keyword} onSearch={handleSearch} />
          <AvailableJobList
            jobs={paginatedJobs}
            onJobSelect={handleJobSelect}
          />
          <JobPagination
            currentPage={
              currentPage > totalPages && totalPages > 0
                ? totalPages
                : currentPage
            }
            totalPages={totalPages}
            onPageChange={handlePageChange}
          />
        </div>
      </main>
      <Separator orientation='vertical' className='mx-2 hidden md:block' />
      <div className='flex w-[40%] flex-col overflow-hidden bg-gray-100/50'>
        <div className='flex-1'>
          <div className='flex items-center justify-between'>
            {selectedJob?.commandList.map(command => (
              <div key={command.commandId}>{command.commandTitle}</div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
};

export default JobManagementPage;
