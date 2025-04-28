import { useParams } from 'react-router-dom';

import SchedulerMonitoringLayout from '@/components/Layout/SchedulerMonitoringLayout';
import { Schedule } from '@/types/scheduler';

import DebugMode from './components/DebugMode';
import JobDisplay from './components/JobDisplay';

const dummySchedule: Schedule = {
  scheduleId: 'schedule-123',
  createdAt: '2025-04-27T00:00:00Z',
  title: '일일 데이터 동기화 스케줄',
  description: '매일 자정 실행되는 데이터 동기화 및 처리 작업',
  userId: 'user-abc',
  status: 'error',
  jobList: [
    {
      jobId: 'job-001',
      title: '데이터 로드 (Source A)',
      description: 'Source A에서 데이터 로드',
      createdAt: '2025-04-27T00:01:00Z',
      commandList: [
        {
          commandId: 'cmd-001-1',
          commandTitle: 'API 연결',
          commandStatus: 'success',
        },
        {
          commandId: 'cmd-001-2',
          commandTitle: '데이터 가져오기 (전체)',
          commandStatus: 'success',
        },
      ],
    },
    {
      jobId: 'job-002',
      title: '데이터 처리 및 변환',
      description: '로드된 데이터 처리',
      createdAt: '2025-04-27T00:05:00Z',
      commandList: [
        {
          commandId: 'cmd-002-1',
          commandTitle: 'A, B, C 컬럼만 가져와줘',
          commandStatus: 'error',
        },
        {
          commandId: 'cmd-002-2',
          commandTitle: '100행까지만 추출해줘',
          commandStatus: 'success',
        },
        {
          commandId: 'cmd-002-3',
          commandTitle: '데이터 유효성 검사',
          commandStatus: 'success',
        },
      ],
    },
    {
      jobId: 'job-003',
      title: '데이터 저장 (Target DB)',
      description: '처리된 데이터를 DB에 저장',
      createdAt: '2025-04-27T00:10:00Z',
      commandList: [
        {
          commandId: 'cmd-003-1',
          commandTitle: 'DB 연결',
          commandStatus: 'success',
        },
        {
          commandId: 'cmd-003-2',
          commandTitle: '테이블 생성 (필요시)',
          commandStatus: 'success',
        },
        {
          commandId: 'cmd-003-3',
          commandTitle: '데이터 삽입',
          commandStatus: 'success',
        },
      ],
    },
  ],
};

const ScheduleDetail = () => {
  const scheduleData = dummySchedule;
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

      <div className='grid grid-cols-1 gap-8 lg:grid-cols-3'>
        <div className='space-y-6 lg:col-span-2'>
          <h2 className='mb-4 border-b pb-2 text-xl font-semibold text-gray-700'>
            Jobs
          </h2>
          {scheduleData.jobList.map(job => (
            <JobDisplay key={job.jobId} job={job} />
          ))}
        </div>

        <div className='lg:col-span-1'>
          <h2 className='invisible mb-4 border-b pb-2 text-xl font-semibold text-gray-700 lg:visible'>
            Details
          </h2>
          <DebugMode schedule={scheduleData} />
        </div>
      </div>
    </SchedulerMonitoringLayout>
  );
};

export default ScheduleDetail;
