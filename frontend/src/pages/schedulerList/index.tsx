import { Link } from 'react-router-dom';

import { Button } from '@/components/ui/button';

const SchedulerListPage = () => {
  return (
    <div className='container mx-auto h-full p-8'>
      <header className='mb-6 flex items-center justify-between gap-3 border-b border-gray-200 pb-4 md:gap-4'>
        <h1 className='text-2xl font-bold'>Scheduler List</h1>

        <Link to={`/scheduler-monitoring/create`}>
          <Button>Create Schedule</Button>
        </Link>
      </header>
    </div>
  );
};

export default SchedulerListPage;
