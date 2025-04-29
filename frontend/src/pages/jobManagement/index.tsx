import { useCallback, useMemo, useState } from 'react';

import { Separator } from '@radix-ui/react-separator';
import { useSearchParams } from 'react-router-dom';

import { Button } from '@/components/ui/button';
import { Job } from '@/types/scheduler';

import AvailableJobList from '../createScheduler/components/AvailableJobList';
import JobPagination from '../createScheduler/components/JobPagination';
import JobSearchInput from '../createScheduler/components/JobSearchInput';
import { allDummyJobs } from '../createScheduler/data';
import CommandItem from './components/CommandItem';

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
      <main className='flex h-full w-[60%] flex-col gap-6 p-8'>
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
            selectedJob={selectedJob}
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
      <div className='flex w-[40%] flex-col overflow-hidden bg-gray-100/50 p-8'>
        <section className='flex grow flex-col gap-2'>
          <div className='flex items-center justify-between gap-2'>
            <p className='text-lg font-bold'>{selectedJob?.title}</p>
          </div>
          <div className='mt-4 flex flex-col gap-2'>
            {selectedJob?.commandList.map(command => (
              <CommandItem
                key={command.commandId}
                commandTitle={command.commandTitle}
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
