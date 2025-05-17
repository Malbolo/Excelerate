import { MousePointerClick } from 'lucide-react';
import { useSearchParams } from 'react-router-dom';

import { JobManagement, useGetJobList } from '@/apis/jobManagement';
import CustomPagination from '@/components/Pagination';
import { ResizableHandle, ResizablePanel, ResizablePanelGroup } from '@/components/ui/resizable';

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
    size: 6,
    mine: true,
  });

  const { total, jobs } = jobList;

  const handleJobSelect = async (job: JobManagement) => {
    const newSearchParams = new URLSearchParams(searchParams.toString());
    newSearchParams.set('selectedJob', job.id);
    setSearchParams(newSearchParams);
  };

  return (
    <div className='bg-gradient relative flex h-screen w-full flex-row'>
      <ResizablePanelGroup direction='horizontal'>
        <ResizablePanel>
          <main className='flex h-full flex-col justify-baseline gap-6 p-8'>
            <header className='flex items-baseline gap-3'>
              <h1 className='text-lg font-bold whitespace-nowrap'>Job Management</h1>
              <p className='text-accent-foreground truncate text-xs'>
                You can view, edit, and delete the details of the job you created
              </p>
            </header>
            <div className='@container flex h-full w-full flex-col overflow-y-auto'>
              <div className='mb-4'>
                <JobSearchInput />
              </div>
              <div className='flex flex-1 flex-col gap-4 overflow-y-auto'>
                <JobList selectedJobId={selectedJobId} onJobSelect={handleJobSelect} jobs={jobs} />
                {jobs.length > 0 && <CustomPagination totalPages={total} />}
              </div>
            </div>
          </main>
        </ResizablePanel>

        <ResizableHandle withHandle />

        <ResizablePanel minSize={40} maxSize={70} defaultSize={50}>
          <div className='h-screen w-full border-l bg-[#FAFCFF]'>
            {selectedJobId ? (
              <CommandList selectedJobId={selectedJobId} />
            ) : (
              <div className='animate-scale flex h-full w-full flex-col items-center justify-center gap-2'>
                <MousePointerClick size={20} className='text-accent-foreground' />
                <p className='text-sm'>Select a job to view details</p>
              </div>
            )}
          </div>
        </ResizablePanel>
      </ResizablePanelGroup>
    </div>
  );
};

export default JobManagementPage;
