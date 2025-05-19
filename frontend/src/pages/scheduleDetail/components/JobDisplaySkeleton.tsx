import { Skeleton } from '@/components/ui/skeleton';

const JobDisplaySkeleton = () => {
  return (
    <div className='card-gradient flex w-full items-center justify-between rounded-lg border px-4 py-3'>
      <div className='flex items-center gap-3'>
        <Skeleton className='h-6 w-6 rounded-full' /> {/* Icon Skeleton */}
        <div className='flex flex-col gap-1 overflow-hidden'>
          <Skeleton className='h-5 w-32 md:w-48' /> {/* Title Skeleton */}
        </div>
      </div>
      <div className='flex items-center gap-2'>
        <Skeleton className='h-5 w-20 rounded-full' /> {/* Badge Skeleton */}
        <Skeleton className='h-7 w-7' /> {/* Button Skeleton */}
      </div>
    </div>
  );
};

export default JobDisplaySkeleton;
