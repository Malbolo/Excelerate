import { useParams } from 'react-router-dom';

import DateNavigator from '@/components/DateNavigator';
import SchedulerMonitoringLayout from '@/components/Layout/SchedulerMonitoringLayout';

import CalendarGrid from './components/CalendarGrid';

const SchedulerMonitoringPage = () => {
  const { monthId } = useParams() as { monthId: string };
  const [year, month] = monthId.split('-').map(Number);

  return (
    <SchedulerMonitoringLayout
      title='Scheduler Monitoring'
      description='Track your schedules with date-based and status-based views.'
      backPath='/'
    >
      <div className='flex h-full flex-col gap-2'>
        <DateNavigator />
        <div className='min-h-0 flex-1'>
          <CalendarGrid year={year} month={month} />
        </div>
      </div>
    </SchedulerMonitoringLayout>
  );
};

export default SchedulerMonitoringPage;
