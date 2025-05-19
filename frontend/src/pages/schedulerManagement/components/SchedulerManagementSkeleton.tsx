import { Skeleton } from '@/components/ui/skeleton';

const SchedulerManagementSkeleton = () => {
  return (
    <div className='flex h-full w-full flex-col p-8'>
      <div className='mb-4 flex items-baseline justify-between'>
        <div className='flex flex-col gap-2'>
          <Skeleton className='h-7 w-64' />
          <Skeleton className='h-4 w-96' />
        </div>
        <Skeleton className='h-10 w-32' />
      </div>

      <div className='card-gradient rounded-md'>
        <div className='flex items-center p-4'>
          <Skeleton className='mr-4 h-6 w-6 flex-shrink-0' />
          <Skeleton className='h-6 w-1/4 flex-grow' />
          <Skeleton className='ml-4 h-6 w-1/6 flex-grow' />
          <Skeleton className='ml-4 h-6 w-1/6 flex-grow' />
          <Skeleton className='ml-4 h-6 w-1/6 flex-grow' />
          <Skeleton className='ml-4 h-6 w-1/6 flex-grow' />
          <Skeleton className='ml-4 h-6 w-24 flex-shrink-0' />
        </div>

        {[...Array(5)].map((_, index) => (
          <div key={index} className='flex items-center p-4'>
            <Skeleton className='mr-4 h-8 w-6 flex-shrink-0' />
            <Skeleton className='h-8 w-1/4 flex-grow' />
            <Skeleton className='ml-4 h-8 w-1/6 flex-grow' />
            <Skeleton className='ml-4 h-8 w-1/6 flex-grow' />
            <Skeleton className='ml-4 h-8 w-1/6 flex-grow' />
            <Skeleton className='ml-4 h-8 w-1/6 flex-grow' />
            <Skeleton className='ml-4 h-8 w-1/6 flex-grow' />
            <Skeleton className='ml-4 h-8 w-24 flex-shrink-0' />
          </div>
        ))}
      </div>
    </div>
  );
};

export default SchedulerManagementSkeleton;
