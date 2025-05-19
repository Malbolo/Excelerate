import { ArrowLeftIcon, Calendar, Hash, XCircle } from 'lucide-react';
import { useParams } from 'react-router-dom';

import { useGetRunDetail } from '@/apis/schedulerMonitoring';
import SchedulerMonitoringLayout from '@/components/Layout/SchedulerMonitoringLayout';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import useInternalRouter from '@/hooks/useInternalRouter';
import { Status } from '@/types/job';

import DebugMode from './components/DebugMode';
import JobDisplay from './components/JobDisplay';
import StatusIcon from './components/StatusIcon';

const ScheduleDetail = () => {
  const { runId, scheduleId, dayId } = useParams() as {
    runId: string;
    scheduleId: string;
    dayId: string;
  };

  const { goBack } = useInternalRouter();

  const { data: scheduleData } = useGetRunDetail(scheduleId, runId);

  if (!scheduleData) {
    return (
      <SchedulerMonitoringLayout title='Loading...' backPath={`/scheduler-monitoring/day/${dayId}`}>
        <div className='text-muted-foreground flex h-40 items-center justify-center'>Loading...</div>
      </SchedulerMonitoringLayout>
    );
  }

  return (
    <div className='bg-gradient relative flex h-full w-full flex-col'>
      <main className='flex h-full flex-col justify-baseline gap-6 p-8'>
        <div className='flex items-center gap-4'>
          <Button variant='ghost' size='sm' onClick={goBack} className='flex items-center gap-2'>
            <ArrowLeftIcon className='h-4 w-4' />
            Back
          </Button>
        </div>
        <header className='flex items-baseline gap-3'>
          <h1 className='text-lg font-bold whitespace-nowrap'>Schedule Details</h1>
          <p className='text-accent-foreground truncate text-xs'>
            View detailed information about the schedule execution and its jobs.
          </p>
        </header>

        <div className='@container flex h-full w-full flex-col overflow-y-auto'>
          {/* Schedule Info Card */}
          <div className='bg-card mb-6 rounded-xl border p-6'>
            <div className='flex w-full flex-col justify-between gap-2'>
              <div className='pb-2'>
                <span className='flex w-full justify-between pb-1'>
                  <p className='text-foreground text-base font-bold'>{scheduleData.title}</p>
                  <Badge variant='outline'>{new Date(scheduleData.start_time).toLocaleString()}</Badge>
                </span>
              </div>

              <div className='flex flex-wrap items-center gap-x-5 gap-y-2 border-t pt-3'>
                <div className='flex items-center'>
                  <Hash className='text-muted-foreground mr-1.5 h-3.5 w-3.5 flex-shrink-0' />
                  <span className='bg-muted text-muted-foreground ring-muted-foreground/20 inline-block max-w-[120px] truncate rounded px-2 py-0.5 text-xs font-medium ring-1 ring-inset sm:max-w-[150px]'>
                    {scheduleData.schedule_id}
                  </span>
                </div>
                <div className='flex items-center'>
                  <Calendar className='text-muted-foreground mr-1.5 h-3.5 w-3.5 flex-shrink-0' />
                  <span className='bg-muted text-muted-foreground ring-muted-foreground/20 inline-block max-w-[120px] truncate rounded px-2 py-0.5 text-xs font-medium ring-1 ring-inset sm:max-w-[150px]'>
                    {new Date(scheduleData.start_time).toLocaleDateString()}
                  </span>
                </div>
                <div className='flex items-center gap-2'>
                  <StatusIcon status={scheduleData.status as Status} />
                  <span
                    className={`inline-block rounded px-2 py-0.5 text-xs font-medium capitalize ${
                      scheduleData.status === 'error'
                        ? 'bg-destructive/10 text-destructive ring-destructive/20 ring-1'
                        : scheduleData.status === 'success'
                          ? 'bg-green-100 text-green-700 ring-1 ring-green-200'
                          : 'bg-muted text-muted-foreground ring-muted-foreground/20 ring-1'
                    } `}
                  >
                    {scheduleData.status}
                  </span>
                </div>
              </div>
            </div>
          </div>

          {/* Jobs and Error Logs Grid */}
          <div className='grid grid-cols-1 gap-8 md:grid-cols-2'>
            <div className='space-y-6'>
              <div className='flex items-center gap-2'>
                <h2 className='text-foreground text-base font-bold'>Jobs</h2>
              </div>
              <div className='space-y-4'>
                {scheduleData.jobs.map(job => (
                  <JobDisplay key={job.id} status={job.status} title={job.title} job={job} />
                ))}
              </div>
            </div>

            <div className='space-y-6'>
              <div className='flex items-center gap-2'>
                <XCircle className='text-destructive h-4 w-4' />
                <h2 className='text-foreground text-base font-bold'>Error Logs</h2>
              </div>
              <div className='space-y-4'>
                {scheduleData.jobs.map(
                  job => job.error_log && <DebugMode key={job.id} jobs={job.error_log} jobTitle={job.title} />,
                )}
              </div>
            </div>
          </div>
        </div>
      </main>
    </div>
  );
};

export default ScheduleDetail;
