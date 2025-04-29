import { useCallback, useMemo, useState } from 'react';

import { useSearchParams } from 'react-router-dom';

import SchedulerMonitoringLayout from '@/components/Layout/SchedulerMonitoringLayout';
import { Button } from '@/components/ui/button';
import { Separator } from '@/components/ui/separator';
import { Job } from '@/types/scheduler';

import AvailableJobList from './components/AvailableJobList';
import CreateScheduleModal from './components/CreateScheduleModal';
import JobPagination from './components/JobPagination';
import JobSearchInput from './components/JobSearchInput';
import SelectedJobList from './components/SelectedJobList';
import { allDummyJobs } from './data';

const ITEMS_PER_PAGE = 6;

const CreateSchedulerPage = () => {
  const [searchParams, setSearchParams] = useSearchParams();

  const [selectedJobs, setSelectedJobs] = useState<Job[]>([]);
  const [isModalOpen, setIsModalOpen] = useState(false);

  const { keyword, currentPage } = useMemo(() => {
    const keyword = searchParams.get('keyword') || '';
    const page = parseInt(searchParams.get('page') || '1', 10);
    return { keyword, currentPage: page };
  }, [searchParams]);

  const handleSearch = useCallback(
    (newKeyword: string) => {
      setSearchParams(
        prev => {
          prev.set('keyword', newKeyword);
          prev.set('page', '1');
          return prev;
        },
        { replace: true },
      );
    },
    [setSearchParams],
  );

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

  const handleJobSelect = useCallback((job: Job, checked: boolean) => {
    setSelectedJobs(prev =>
      checked
        ? prev.some(j => j.jobId === job.jobId)
          ? prev
          : [...prev, job]
        : prev.filter(j => j.jobId !== job.jobId),
    );
  }, []);

  const handleJobOrderChange = useCallback((newOrder: Job[]) => {
    setSelectedJobs(newOrder);
  }, []);

  const handleJobDeselect = useCallback((jobId: string) => {
    setSelectedJobs(prev => prev.filter(job => job.jobId !== jobId));
  }, []);

  const selectedJobIds = useMemo(
    () => new Set(selectedJobs.map(job => job.jobId)),
    [selectedJobs],
  );

  const currentYear = new Date().getFullYear();
  const currentMonth = new Date().getMonth() + 1;
  const layoutTitle = `Create Schedule`;
  const backPath = `/scheduler-monitoring/month/${currentYear}-${String(currentMonth).padStart(2, '0')}`;

  return (
    <SchedulerMonitoringLayout title={layoutTitle} backPath={backPath}>
      <div className='flex h-[calc(100vh-150px)] flex-col md:flex-row md:gap-6'>
        <div className='flex w-full flex-col overflow-hidden md:w-1/2'>
          <JobSearchInput initialKeyword={keyword} onSearch={handleSearch} />
          <AvailableJobList
            jobs={paginatedJobs}
            selectedJobIds={selectedJobIds}
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
        <Separator orientation='vertical' className='mx-2 hidden md:block' />
        <div className='mt-6 flex w-full flex-col overflow-hidden md:mt-0 md:w-1/2'>
          <SelectedJobList
            selectedJobs={selectedJobs}
            onJobDeselect={handleJobDeselect}
            onOrderChange={handleJobOrderChange}
          />
          <div className='mt-4 flex-shrink-0'>
            <Button
              className='w-full'
              disabled={selectedJobs.length === 0}
              onClick={() => setIsModalOpen(true)}
            >
              Done ({selectedJobs.length})
            </Button>
          </div>
        </div>
      </div>

      <CreateScheduleModal
        isOpen={isModalOpen}
        onOpenChange={setIsModalOpen}
        selectedJobs={selectedJobs}
      />
    </SchedulerMonitoringLayout>
  );
};

export default CreateSchedulerPage;
