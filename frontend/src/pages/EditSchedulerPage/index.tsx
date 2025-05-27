import { useMemo, useState } from 'react';

import { useParams, useSearchParams } from 'react-router-dom';

import { JobManagement, useGetJobList } from '@/apis/jobManagement';
import { useGetScheduleDetail } from '@/apis/schedulerManagement';
import SchedulerMonitoringLayout from '@/components/Layout/SchedulerMonitoringLayout';
import CustomPagination from '@/components/Pagination';
import ScheduleDialog from '@/components/ScheduleDialog';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { ResizableHandle, ResizablePanel, ResizablePanelGroup } from '@/components/ui/resizable';

import JobList from '../createScheduler/components/JobList';
import JobSearchInput from '../createScheduler/components/JobSearchInput';
import SelectedJobList from '../createScheduler/components/SelectedJobList';

const CreateSchedulerPage = () => {
  const { scheduleId } = useParams() as { scheduleId: string };
  const { data: scheduleDetail } = useGetScheduleDetail(scheduleId);

  const { jobs: responseJobs } = scheduleDetail;

  const [selectedJobs, setSelectedJobs] = useState<JobManagement[]>(responseJobs as JobManagement[]);
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
    size: 6,
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

  const selectedJobIds = useMemo(() => new Set(selectedJobs.map(job => job.id)), [selectedJobs]);

  return (
    <SchedulerMonitoringLayout
      title='Edit Schedule'
      backPath={'/scheduler-management'}
      description='Edit the schedule to include the jobs you want to run.'
    >
      <div className='bg-gradient relative mx-auto flex h-[calc(100vh-120px)] w-full border-t'>
        <ResizablePanelGroup direction='horizontal'>
          <ResizablePanel>
            <div className='mx-auto flex h-full w-full grow-0 flex-col justify-between gap-4'>
              <div className='@container flex flex-1 flex-col gap-4 overflow-hidden p-8'>
                <JobSearchInput />
                <div className='flex flex-1 flex-col justify-between overflow-y-auto'>
                  <div className='flex flex-col gap-4'>
                    <JobList selectedJobIds={selectedJobIds} onJobSelect={handleJobSelect} jobs={jobs} />
                  </div>
                  {jobs.length > 0 && (
                    <div className='mt-4 flex-shrink-0'>
                      <CustomPagination totalPages={total} />
                    </div>
                  )}
                </div>
              </div>
            </div>
          </ResizablePanel>

          <ResizableHandle withHandle />

          <ResizablePanel minSize={40} maxSize={70} defaultSize={50}>
            <div className='h-full w-full border-l bg-[#FAFCFF]'>
              <div className='flex h-full flex-col p-8'>
                <header className='mb-6 flex items-center justify-between'>
                  <div className='flex flex-col gap-2'>
                    <h2 className='text-lg font-bold'>Selected Jobs</h2>
                    <Badge variant='secondary' className='text-xs'>
                      {selectedJobs.length} jobs selected
                    </Badge>
                  </div>
                  <Button disabled={selectedJobs.length === 0} onClick={() => setIsModalOpen(true)}>
                    Done
                  </Button>
                </header>
                <div className='flex flex-1 flex-col overflow-y-auto'>
                  <div className='flex h-full flex-col gap-4'>
                    <SelectedJobList
                      selectedJobs={selectedJobs}
                      handleJobDeselect={handleJobDeselect}
                      handleJobOrderChange={handleJobOrderChange}
                    />
                  </div>
                </div>
              </div>
            </div>
          </ResizablePanel>
        </ResizablePanelGroup>
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
