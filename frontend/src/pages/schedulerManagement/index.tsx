import { Link } from 'react-router-dom';

import { Button } from '@/components/ui/button';
import ScheduleTable from '@/pages/schedulerManagement/components/ScheduleTable';

const SchedulerManagement = () => {
  return (
    <div className='mx-auto p-8'>
      <div className='mb-8 flex items-center justify-between'>
        <div>
          <h1 className='mb-4 text-2xl font-bold'>Schedules (Table View)</h1>
          <p className='text-gray-600'>
            Manage your schedules here. Add, edit, or delete schedules as
            needed.
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
