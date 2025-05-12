import { useParams } from 'react-router-dom';

import { useGetRunDetail } from '@/apis/schedulerMonitoring';
import SchedulerMonitoringLayout from '@/components/Layout/SchedulerMonitoringLayout';

import DebugMode from './components/DebugMode';
import JobDisplay from './components/JobDisplay';

const ScheduleDetail = () => {
  const { runId, scheduleId, dayId } = useParams() as {
    runId: string;
    scheduleId: string;
    dayId: string;
  };

  const { data: scheduleData } = useGetRunDetail(scheduleId, runId);

  return (
    <SchedulerMonitoringLayout
      title={scheduleData.title}
      backPath={`/scheduler-monitoring/day/${dayId}`}
    >
      <div className='mb-8 rounded-lg bg-white p-6 shadow'>
        <p className='mt-1 text-sm text-gray-500'>{scheduleData.title}</p>
        <div className='mt-2 text-xs text-gray-400'>
          <span>ID: {scheduleData.schedule_id} | </span>
          <span>
            Created: {new Date(scheduleData.start_time).toLocaleString()} |{' '}
          </span>
          <span>
            Status:
            <span
              className={`font-medium ${scheduleData.status === 'error' ? 'text-red-500' : 'text-green-500'}`}
            >
              {scheduleData.status}
            </span>
          </span>
        </div>
      </div>

      <div className='grid grid-cols-2 gap-8 pb-8'>
        <div className='space-y-6'>
          <h2 className='mb-4 border-b pb-2 text-xl font-semibold text-gray-700'>
            Jobs
          </h2>
          {scheduleData.jobs.map(job => (
            <JobDisplay
              key={job.id}
              status={job.status}
              title={job.title}
              job={job}
            />
          ))}
        </div>

        <div className='space-y-6'>
          <h2 className='mb-4 border-b pb-2 text-xl font-semibold text-gray-700'>
            Details
          </h2>
          {scheduleData.jobs.map(
            job =>
              job.error_log && <DebugMode key={job.id} error={job.error_log} />,
          )}
        </div>
      </div>
    </SchedulerMonitoringLayout>
  );
};

export default ScheduleDetail;
