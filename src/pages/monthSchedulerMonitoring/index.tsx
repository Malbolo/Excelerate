import { Link, useParams } from 'react-router-dom';

import DateNavigator from '@/components/DateNavigator';
import SchedulerMonitoringLayout from '@/components/Layout/SchedulerMonitoringLayout';
import { Button } from '@/components/ui/button';

import CalendarGrid from './components/CalendarGrid';

// Info : monthId 형식: YYYY-MM

const SchedulerMonitoringPage = () => {
  const { monthId } = useParams() as { monthId: string };
  const [year, month] = monthId.split('-').map(Number);

  return (
    <SchedulerMonitoringLayout
      title={`${year}년 ${month}월 스케줄 모니터링`}
      backPath='/'
    >
      <DateNavigator />
      <CalendarGrid year={year} month={month} />
      <div className='absolute right-0 bottom-0 mt-4 rounded-lg'>
        <Link to={`/scheduler-monitoring/create`}>
          <Button>Create Schedule</Button>
        </Link>
      </div>
    </SchedulerMonitoringLayout>
  );
};

export default SchedulerMonitoringPage;
