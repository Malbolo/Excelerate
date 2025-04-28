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

  // todo: zustand로 선택된 작업 상태 관리 예정
  const [selectedJobs, setSelectedJobs] = useState<Job[]>([]);
  const [isModalOpen, setIsModalOpen] = useState(false);

  const { keyword, currentPage } = useMemo(() => {
    const keyword = searchParams.get('keyword') || '';
    const page = parseInt(searchParams.get('page') || '1', 10);
    const validPage = Math.max(1, isNaN(page) ? 1 : page);
    return { keyword, currentPage: validPage };
  }, [searchParams]);

  // Info : 검색 기능 함수
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

  // Delete : 더미데이터를 위한 변수, 추후 삭제 예정, 실제 데이터로 변경 필요
  const filteredJobs = useMemo(() => {
    if (!keyword) return allDummyJobs;
    const lowerCaseKeyword = keyword.toLowerCase();
    return allDummyJobs.filter(
      job =>
        job.title.toLowerCase().includes(lowerCaseKeyword) ||
        job.description.toLowerCase().includes(lowerCaseKeyword),
    );
  }, [keyword]);

  // Delete : 더미데이터를 위한 변수, 추후 삭제 예정, 실제 데이터로 변경 필요
  const { paginatedJobs, totalPages } = useMemo(() => {
    const total = Math.ceil(filteredJobs.length / ITEMS_PER_PAGE);
    const adjustedPage = Math.min(currentPage, total > 0 ? total : 1);
    const startIndex = (adjustedPage - 1) * ITEMS_PER_PAGE;
    const endIndex = startIndex + ITEMS_PER_PAGE;
    const jobs = filteredJobs.slice(startIndex, endIndex);
    return { paginatedJobs: jobs, totalPages: total };
  }, [filteredJobs, currentPage]);

  // Info : 페이지 변경 기능 함수
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

  // Info : 작업 선택 기능 함수
  const handleJobSelect = useCallback((job: Job, checked: boolean) => {
    setSelectedJobs(prev =>
      checked
        ? prev.some(j => j.jobId === job.jobId)
          ? prev
          : [...prev, job]
        : prev.filter(j => j.jobId !== job.jobId),
    );
  }, []);

  // Info : 작업 순서 변경 기능 함수
  // todo: 작업 순서 변경 기능 zustand로 이동 예정
  const handleJobOrderChange = useCallback((newOrder: Job[]) => {
    setSelectedJobs(newOrder);
  }, []);

  // Info : 작업 선택 해제 기능 함수
  // todo: 작업 선택 해제 기능 zustand로 이동 예정
  const handleJobDeselect = useCallback((jobId: string) => {
    setSelectedJobs(prev => prev.filter(job => job.jobId !== jobId));
  }, []);

  // Info : 선택된 작업 ID 목록 생성 기능 함수
  // Delete : 더미데이터를 위해 사용, 추후에는 실제 jobId 사용 필요
  const selectedJobIds = useMemo(
    () => new Set(selectedJobs.map(job => job.jobId)),
    [selectedJobs],
  );

  const currentYear = new Date().getFullYear();
  const currentMonth = new Date().getMonth() + 1;
  const layoutTitle = `스케줄 생성`;
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

        <div className='mt-6 flex w-full flex-col md:mt-0 md:w-1/2'>
          <SelectedJobList
            selectedJobs={selectedJobs}
            onJobDeselect={handleJobDeselect}
            onOrderChange={handleJobOrderChange}
          />
          <div className='mt-4'>
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
