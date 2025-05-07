import { format, parse } from 'date-fns';
import { enUS } from 'date-fns/locale';
import { useParams } from 'react-router-dom';

import { useGetDaySchedules } from '@/apis/schedulerMonitoring';
import DateNavigator from '@/components/DateNavigator';
import SchedulerMonitoringLayout from '@/components/Layout/SchedulerMonitoringLayout';

import ScheduleList from './components/ScheduleList';

const DaySchedulePage = () => {
  const { dayId } = useParams() as { dayId: string };

  const [year, month, date] = dayId.split('-');
  const parsedDate = parse(dayId, 'yyyy-MM-dd', new Date());
  const title = `Daily Schedule - ${format(parsedDate, 'MM/dd/yyyy', {
    locale: enUS,
  })}`;
  const backPath = `/scheduler-monitoring/month/${year}-${month}`;

  const { data: daySchedules } = useGetDaySchedules(year, month, date);

  const { success, failed, pending } = daySchedules;

  return (
    <SchedulerMonitoringLayout title={title} backPath={backPath}>
      <DateNavigator />
      <div className='mt-8 grid grid-cols-1 gap-6 md:grid-cols-3'>
        <div className='flex flex-col overflow-hidden rounded-lg border border-gray-200 bg-white shadow-sm'>
          <div className='border-b border-yellow-200 bg-yellow-50 px-5 py-4'>
            <h2 className='text-lg font-semibold text-yellow-800'>Pending</h2>
          </div>
          <div className='flex-grow p-4'>
            <ScheduleList items={success} />
          </div>
        </div>

        <div className='flex flex-col overflow-hidden rounded-lg border border-gray-200 bg-white shadow-sm'>
          <div className='border-b border-green-200 bg-green-50 px-5 py-4'>
            <h2 className='text-lg font-semibold text-green-800'>Success</h2>
          </div>
          <div className='flex-grow p-4'>
            <ScheduleList items={failed} />
          </div>
        </div>

        <div className='flex flex-col overflow-hidden rounded-lg border border-gray-200 bg-white shadow-sm'>
          <div className='border-b border-red-200 bg-red-50 px-5 py-4'>
            <h2 className='text-lg font-semibold text-red-800'>Error</h2>
          </div>
          <div className='flex-grow p-4'>
            <ScheduleList items={pending} />
          </div>
        </div>
      </div>
    </SchedulerMonitoringLayout>
  );
};

export default DaySchedulePage;
