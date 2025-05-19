import { useParams } from 'react-router-dom';

import { useDeleteMonthCache, useGetMonthSchedules } from '@/apis/schedulerMonitoring';
import DateNavigator from '@/components/DateNavigator';
import SchedulerMonitoringLayout from '@/components/Layout/SchedulerMonitoringLayout';

import CalendarGrid from './components/CalendarGrid';

const SchedulerMonitoringPage = () => {
  const { monthId } = useParams() as { monthId: string };
  const [year, month] = monthId.split('-').map(Number);

  const { dataUpdatedAt } = useGetMonthSchedules(year.toString(), month.toString());

  const deleteMonthCache = useDeleteMonthCache();

  const handleReload = () => {
    deleteMonthCache({ year: year.toString(), month: month.toString() });
  };

  return (
    <SchedulerMonitoringLayout
      title='Scheduler Monitoring'
      description='Track your schedules with date-based and status-based views.'
      backPath='/'
      onReload={handleReload}
      updatedAt={dataUpdatedAt}
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
