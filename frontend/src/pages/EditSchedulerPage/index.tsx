import { useMemo, useState } from 'react';

import { useParams, useSearchParams } from 'react-router-dom';

import { JobManagement, useGetJobList } from '@/apis/jobManagement';
import { useGetScheduleDetail } from '@/apis/schedulerManagement';
import SchedulerMonitoringLayout from '@/components/Layout/SchedulerMonitoringLayout';
import { Button } from '@/components/ui/button';
import { Separator } from '@/components/ui/separator';

import AvailableJobList from '../createScheduler/components/AvailableJobList';
import JobPagination from '../createScheduler/components/JobPagination';
import JobSearchInput from '../createScheduler/components/JobSearchInput';
import ScheduleDialog from '../createScheduler/components/ScheduleDialog';
import SelectedJobList from '../createScheduler/components/SelectedJobList';

const CreateSchedulerPage = () => {
  const { scheduleId } = useParams() as { scheduleId: string };
  const { data: scheduleDetail } = useGetScheduleDetail(scheduleId);

  const { jobs: responseJobs } = scheduleDetail;

  const [selectedJobs, setSelectedJobs] =
    useState<JobManagement[]>(responseJobs);
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [searchParams] = useSearchParams();

  const currentPage = parseInt(searchParams.get('page') || '1', 10);
  const types = searchParams.get('types') || '';
  const title = searchParams.get('title') || '';
  const name = searchParams.get('name') || '';

  const { data: jobList } = useGetJobList({
    page: currentPage,
    title,
    types,
    name,
    mine: false,
  });

  const { total, jobs } = jobList;

  const handleJobSelect = (job: JobManagement, checked: boolean) => {
    setSelectedJobs(prev =>
      checked
        ? prev.some(j => j.id === job.id)
          ? prev
          : [...prev, job]
        : prev.filter(j => j.id !== job.id),
    );
  };

  const handleJobDeselect = (jobId: string) => {
    setSelectedJobs(prev => prev.filter(job => job.id !== jobId));
  };

  const handleJobOrderChange = (newOrder: JobManagement[]) => {
    setSelectedJobs(newOrder);
  };

  const selectedJobIds = useMemo(
    () => new Set(selectedJobs.map(job => job.id)),
    [selectedJobs],
  );

  return (
    <SchedulerMonitoringLayout
      title={'Edit Schedule'}
      backPath={'/scheduler-management'}
    >
      <div className='flex h-[calc(100vh-150px)] flex-col md:flex-row md:gap-6'>
        <div className='flex w-full flex-col overflow-hidden md:w-1/2'>
          <JobSearchInput />
          <AvailableJobList
            selectedJobIds={selectedJobIds}
            onJobSelect={handleJobSelect}
            jobs={jobs}
          />
          <JobPagination total={total} />
        </div>
        <Separator orientation='vertical' className='mx-2 hidden md:block' />
        <div className='mt-6 flex w-full flex-col overflow-hidden md:mt-0 md:w-1/2'>
          <SelectedJobList
            selectedJobs={selectedJobs}
            handleJobDeselect={handleJobDeselect}
            handleJobOrderChange={handleJobOrderChange}
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

      <ScheduleDialog
        isOpen={isModalOpen}
        onOpenChange={setIsModalOpen}
        selectedJobs={selectedJobs}
        scheduleDetail={scheduleDetail}
      />
    </SchedulerMonitoringLayout>
  );
};

export default CreateSchedulerPage;
