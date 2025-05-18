import { useState } from 'react';

import { useSearchParams } from 'react-router-dom';

import { JobManagement, useGetJobList } from '@/apis/jobManagement';
import SchedulerMonitoringLayout from '@/components/Layout/SchedulerMonitoringLayout';
import CustomPagination from '@/components/Pagination';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { ResizableHandle, ResizablePanel, ResizablePanelGroup } from '@/components/ui/resizable';

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

  const selectedJobIds = new Set(selectedJobs.map(job => job.id));

  const currentYear = new Date().getFullYear();
  const currentMonth = new Date().getMonth() + 1;
  const layoutTitle = `Create Schedule`;
  const backPath = `/scheduler-monitoring/month/${currentYear}-${String(currentMonth).padStart(2, '0')}`;

  return (
    <SchedulerMonitoringLayout
      title={layoutTitle}
      backPath={backPath}
      description='Create a new schedule to include the jobs you want to run.'
    >
      <div className='bg-gradient relative flex h-[calc(100vh-120px)] w-full'>
        <ResizablePanelGroup direction='horizontal'>
          <ResizablePanel>
            <div className='mx-auto flex h-full w-full grow-0 flex-col justify-between gap-4 p-8'>
              <div className='@container flex flex-1 flex-col gap-4 overflow-hidden'>
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

      <ScheduleDialog isOpen={isModalOpen} onOpenChange={setIsModalOpen} selectedJobs={selectedJobs} />
    </SchedulerMonitoringLayout>
  );
};

export default CreateSchedulerPage;
