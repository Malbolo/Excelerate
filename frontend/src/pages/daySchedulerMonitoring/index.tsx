import { format, parse } from 'date-fns';
import { enUS } from 'date-fns/locale';
import { CheckCircle, Clock, XCircle } from 'lucide-react';
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
      <div className='grid h-full grid-cols-1 gap-4 overflow-y-auto px-4 pt-2 md:grid-cols-3 md:px-6'>
        <div className='bg-card flex flex-col overflow-hidden rounded-xl border border-yellow-400'>
          <div className='border-b border-yellow-400 bg-yellow-50/50 px-5 py-3.5'>
            <div className='flex items-center justify-between'>
              <div className='flex items-center gap-2'>
                <Clock className='h-4 w-4 text-yellow-600' />
                <h2 className='text-base font-bold text-yellow-600'>Pending</h2>
              </div>
              <span className='rounded-full bg-yellow-100 px-2.5 py-0.5 text-sm font-medium text-yellow-700'>
                {pending.length}
              </span>
            </div>
          </div>
          <div className='flex-1 px-4 py-1'>
            <ScheduleList items={pending} />
          </div>
        </div>

        <div className='bg-card flex flex-col overflow-hidden rounded-xl border border-green-400'>
          <div className='border-b border-green-400 bg-green-50/50 px-5 py-3.5'>
            <div className='flex items-center justify-between'>
              <div className='flex items-center gap-2'>
                <CheckCircle className='h-4 w-4 text-green-700' />
                <h2 className='text-base font-bold text-green-700'>Success</h2>
              </div>
              <span className='rounded-full bg-green-100 px-2.5 py-0.5 text-sm font-medium text-green-700'>
                {success.length}
              </span>
            </div>
          </div>
          <div className='flex-1 px-4 py-1'>
            <ScheduleList items={success} />
          </div>
        </div>

        <div className='bg-card flex flex-col overflow-hidden rounded-xl border border-red-300'>
          <div className='border-b border-red-300 bg-red-50/50 px-5 py-3.5'>
            <div className='flex items-center justify-between'>
              <div className='flex items-center gap-2'>
                <XCircle className='h-4 w-4 text-red-600' />
                <h2 className='text-base font-bold text-red-600'>Error</h2>
              </div>
              <span className='rounded-full bg-red-100 px-2.5 py-0.5 text-sm font-medium text-red-700'>
                {failed.length}
              </span>
            </div>
          </div>
          <div className='flex-1 px-4 py-1'>
            <ScheduleList items={failed} />
          </div>
        </div>
      </div>
    </SchedulerMonitoringLayout>
  );
};

export default DaySchedulePage;
