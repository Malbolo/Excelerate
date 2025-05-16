import { useState } from 'react';

import { useSearchParams } from 'react-router-dom';

import { JobManagement, useGetJobList } from '@/apis/jobManagement';
import SchedulerMonitoringLayout from '@/components/Layout/SchedulerMonitoringLayout';
import CustomPagination from '@/components/Pagination';
import { Button } from '@/components/ui/button';
import { Separator } from '@/components/ui/separator';

import JobList from './components/JobList';
import JobSearchInput from './components/JobSearchInput';
import ScheduleDialog from './components/ScheduleDialog';
import SelectedJobList from './components/SelectedJobList';

const CreateSchedulerPage = () => {
  const [selectedJobs, setSelectedJobs] = useState<JobManagement[]>([]);
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
      checked ? (prev.some(j => j.id === job.id) ? prev : [...prev, job]) : prev.filter(j => j.id !== job.id),
    );
  };

  const handleJobDeselect = (jobId: string) => {
    setSelectedJobs(prev => prev.filter(job => job.id !== jobId));
  };

  const handleJobOrderChange = (newOrder: JobManagement[]) => {
    setSelectedJobs(newOrder);
  };

  const selectedJobIds = new Set(selectedJobs.map(job => job.id));

  const currentYear = new Date().getFullYear();
  const currentMonth = new Date().getMonth() + 1;
  const layoutTitle = `Create Schedule`;
  const backPath = `/scheduler-monitoring/month/${currentYear}-${String(currentMonth).padStart(2, '0')}`;

  return (
    <SchedulerMonitoringLayout title={layoutTitle} backPath={backPath}>
      <div className='flex h-[calc(100vh-150px)] flex-col md:flex-row md:gap-6'>
        <div className='flex w-full flex-col overflow-hidden md:w-1/2'>
          <JobSearchInput />
          <JobList selectedJobIds={selectedJobIds} onJobSelect={handleJobSelect} jobs={jobs} />
          <CustomPagination totalPages={total} />
        </div>
        <Separator orientation='vertical' className='mx-2 hidden md:block' />
        <div className='mt-6 flex w-full flex-col overflow-hidden md:mt-0 md:w-1/2'>
          <SelectedJobList
            selectedJobs={selectedJobs}
            handleJobDeselect={handleJobDeselect}
            handleJobOrderChange={handleJobOrderChange}
          />
          <div className='mt-4 flex-shrink-0'>
            <Button className='w-full' disabled={selectedJobs.length === 0} onClick={() => setIsModalOpen(true)}>
              Done ({selectedJobs.length})
            </Button>
          </div>
        </div>
      </div>

      <ScheduleDialog isOpen={isModalOpen} onOpenChange={setIsModalOpen} selectedJobs={selectedJobs} />
    </SchedulerMonitoringLayout>
  );
};

export default CreateSchedulerPage;
