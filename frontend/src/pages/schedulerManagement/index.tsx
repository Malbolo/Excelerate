import { Suspense } from 'react';

import { Link, useSearchParams } from 'react-router-dom';

import { useGetScheduleList } from '@/apis/schedulerManagement';
import CustomPagination from '@/components/Pagination';
import { Button } from '@/components/ui/button';
import { Separator } from '@/components/ui/separator';
import ScheduleTable from '@/pages/schedulerManagement/components/ScheduleTable';

import SchedulerFilterBar, { FREQUENCIES, STATUSES } from './components/SchedulerFilterBar';
import SchedulerManagementSkeleton from './components/SchedulerManagementSkeleton';

const DEFAULT_FREQUENCY = FREQUENCIES.find(f => f.value === 'all')?.value || FREQUENCIES[0].value;
const DEFAULT_STATUS = STATUSES.find(s => s.value === 'all')?.value || STATUSES[0].value;

const SchedulerManagementPage = () => {
  const [searchParams] = useSearchParams();

  const pageParam = searchParams.get('page') || '1';
  const sizeParam = searchParams.get('size') || '10';
  const titleParam = searchParams.get('title');
  const ownerParam = searchParams.get('owner');
  const frequencyParam = searchParams.get('frequency') || DEFAULT_FREQUENCY;
  const statusParam = searchParams.get('status') || DEFAULT_STATUS;

  const apiParams = {
    page: pageParam,
    size: sizeParam,
    title: titleParam || undefined,
    owner: ownerParam || undefined,
    frequency: frequencyParam === 'all' ? undefined : frequencyParam,
    status: statusParam || undefined,
  };

  const { data } = useGetScheduleList(apiParams);
  const { schedules, total_pages } = data;

  return (
    <div className='bg-gradient flex h-full w-full flex-col space-y-6 p-4 sm:p-6 md:p-8'>
      <header className='flex flex-col items-start justify-between gap-4 sm:flex-row sm:items-center'>
        <div>
          <h1 className='text-2xl font-bold tracking-tight text-gray-900 sm:text-3xl'>Scheduler Management</h1>
          <p className='mt-1 text-sm text-gray-600'>
            Manage your schedules here. Add, edit, or delete schedules as needed.
          </p>
        </div>
        <Link to='/scheduler-management/create'>
          <Button className='w-full sm:w-auto'>Add Schedule</Button>
        </Link>
      </header>

      <Separator />

      <SchedulerFilterBar />

      <div className='bg-card overflow-x-auto rounded-lg border'>
        <Suspense fallback={<SchedulerManagementSkeleton />}>
          <ScheduleTable schedules={schedules} />
        </Suspense>
      </div>

      {total_pages > 1 && (
        <div className='mt-auto flex justify-center pt-6'>
          <CustomPagination totalPages={total_pages} />
        </div>
      )}
    </div>
  );
};

export default SchedulerManagementPage;
