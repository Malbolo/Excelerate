import { useParams } from 'react-router-dom';

import SchedulerMonitoringLayout from '@/components/Layout/SchedulerMonitoringLayout';

import { dummySchedules } from '../schedulerManagement/data';
import DebugMode from './components/DebugMode';
import JobDisplay from './components/JobDisplay';

const ScheduleDetail = () => {
  const scheduleData = dummySchedules[0];
  const { dayId } = useParams();

  return (
    <SchedulerMonitoringLayout
      title={scheduleData.title}
      backPath={`/scheduler-monitoring/day/${dayId}`}
    >
      <div className='mb-8 rounded-lg bg-white p-6 shadow'>
        <p className='mt-1 text-sm text-gray-500'>{scheduleData.description}</p>
        <div className='mt-2 text-xs text-gray-400'>
          <span>ID: {scheduleData.scheduleId} | </span>
          <span>
            Created: {new Date(scheduleData.createdAt).toLocaleString()} |{' '}
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
          {scheduleData.jobList.map(job => (
            <JobDisplay key={job.jobId} job={job} />
          ))}
        </div>

        <div className='space-y-6'>
          <h2 className='mb-4 border-b pb-2 text-xl font-semibold text-gray-700'>
            Details
          </h2>
          <DebugMode schedule={scheduleData} />
        </div>
      </div>
    </SchedulerMonitoringLayout>
  );
};

export default ScheduleDetail;
