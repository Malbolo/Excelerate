import { Link } from 'react-router-dom';

import { Button } from '@/components/ui/button';
import ScheduleTable from '@/pages/schedulerManagement/components/ScheduleTable';

const SchedulerManagement = () => {
  return (
    <div className='bg-gradient flex h-full w-full flex-col p-8'>
      <div className='mb-4 flex items-baseline justify-between'>
        <div className='flex items-baseline gap-3'>
          <h1 className='mb-4 text-lg font-bold'>Scheduler Management</h1>
          <p className='text-accent-foreground truncate text-xs'>
            Manage your schedules here. Add, edit, or delete schedules as needed.
          </p>
        </div>
        <Link to='/scheduler-management/create'>
          <Button>Add Schedule</Button>
        </Link>
      </div>
      <ScheduleTable />
    </div>
  );
};

export default SchedulerManagement;
