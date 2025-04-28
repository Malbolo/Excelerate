import { useParams } from 'react-router-dom';

import DateNavigator from '@/components/DateNavigator';
import SchedulerMonitoringLayout from '@/components/Layout/SchedulerMonitoringLayout';
import { DaySchedule } from '@/types/scheduler';

import ScheduleList from './components/ScheduleList';

const mockData: DaySchedule = {
  pending: [
    {
      scheduleId: 'schedule1',
      createdAt: '2025-04-24T09:00:00',
      title: 'KPI Report',
      description: 'Create April KPI report',
      userId: 'user1',
      status: 'pending',
      jobList: [
        {
          jobId: 'job1',
          title: 'Data Collection',
          description: 'Collect and organize KPI data',
          createdAt: '2025-04-24T09:00:00',
          commandList: [
            {
              commandId: 'command1',
              commandTitle: 'Data Collection',
              commandStatus: 'pending',
            },
          ],
        },
      ],
    },
  ],
  success: [
    {
      scheduleId: 'schedule2',
      createdAt: '2025-04-24T11:00:00',
      title: 'CNC Equipment Performance Rate',
      description: 'Equipment performance measurement complete',
      userId: 'user3',
      status: 'success',
      jobList: [
        {
          jobId: 'job2',
          title: 'Performance Measurement',
          description: 'Equipment performance measurement complete',
          createdAt: '2025-04-24T11:00:00',
          commandList: [
            {
              commandId: 'command2',
              commandTitle: 'Performance Measurement',
              commandStatus: 'success',
            },
          ],
        },
      ],
    },
  ],
  error: [
    {
      scheduleId: 'schedule3',
      createdAt: '2025-04-24T12:00:00',
      title: 'Product A Defect Rate',
      description: 'Failed to measure defect rate',
      userId: 'user4',
      status: 'error',
      jobList: [
        {
          jobId: 'job3',
          title: 'Defect Rate Measurement',
          description: 'Measurement equipment error',
          createdAt: '2025-04-24T12:00:00',
          commandList: [
            {
              commandId: 'command3',
              commandTitle: 'Defect Rate Measurement',
              commandStatus: 'error',
            },
          ],
        },
      ],
    },
  ],
};

const DaySchedulePage = () => {
  const { dayId } = useParams() as { dayId: string };

  const day = new Date(dayId);
  const year = day.getFullYear();
  const month = day.getMonth() + 1;
  const date = day.getDate();

  return (
    <SchedulerMonitoringLayout
      title={`${year}년 ${month}월 ${date}일 스케줄 모니터링`}
      backPath={`/scheduler-monitoring/month/${year}-${month}`}
    >
      <DateNavigator />
      <div className='mt-8 grid grid-cols-1 gap-6 md:grid-cols-3'>
        <div className='overflow-hidden rounded-lg border border-gray-200 bg-white shadow-sm'>
          <div className='border-b border-gray-200 bg-yellow-600 px-4 py-3'>
            <h2 className='text-lg font-semibold text-white'>Pending</h2>
          </div>
          <div className='p-4'>
            <ScheduleList items={mockData.pending} />
          </div>
        </div>
        <div className='overflow-hidden rounded-lg border border-gray-200 bg-white shadow-sm'>
          <div className='border-b border-gray-200 bg-green-600 px-4 py-3'>
            <h2 className='text-lg font-semibold text-white'>Success</h2>
          </div>
          <div className='p-4'>
            <ScheduleList items={mockData.success} />
          </div>
        </div>
        <div className='overflow-hidden rounded-lg border border-gray-200 bg-white shadow-sm'>
          <div className='border-b border-gray-200 bg-red-600 px-4 py-3'>
            <h2 className='text-lg font-semibold text-white'>Error</h2>
          </div>
          <div className='p-4'>
            <ScheduleList items={mockData.error} />
          </div>
        </div>
      </div>
    </SchedulerMonitoringLayout>
  );
};

export default DaySchedulePage;
