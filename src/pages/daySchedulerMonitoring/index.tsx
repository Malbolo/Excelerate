import { useParams } from 'react-router-dom';

import { DaySchedule } from '@/types/scheduler';

import { DateNavigator } from './components/DateNavigator';
import ScheduleList from './components/ScheduleList';

const mockData: DaySchedule = {
  pending: [
    {
      batchId: 'batch1',
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
      batchId: 'batch2',
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
      batchId: 'batch3',
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

export default function DaySchedulePage() {
  const { dayId } = useParams<{ dayId: string }>();
  const currentDate =
    dayId && !isNaN(new Date(dayId).getTime()) ? new Date(dayId) : new Date();

  return (
    <div className='container mx-auto min-h-screen bg-gray-50 px-4 py-8'>
      <DateNavigator currentDate={currentDate} />
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
    </div>
  );
}
