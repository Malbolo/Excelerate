import { ChevronLeft, RefreshCw } from 'lucide-react';
import { Link } from 'react-router-dom';

import { Button } from '@/components/ui/button';
import { formatDateTime } from '@/lib/dateFormat';
import { useLocalDate } from '@/store/useLocalDate';

interface SchedulerMonitoringLayoutProps {
  title: string;
  description?: string;
  backPath: string;
  children: React.ReactNode;
  onReload?: () => void;
  updatedAt?: string | null;
}

const SchedulerMonitoringLayout = ({
  title,
  description,
  backPath,
  children,
  onReload,
  updatedAt,
}: SchedulerMonitoringLayoutProps) => {
  const { locale, place } = useLocalDate();
  return (
    <div className='flex h-full w-full flex-col p-6 md:p-8'>
      <div className='mb-4 flex flex-col gap-2 md:flex-row md:items-center md:justify-between'>
        <div className='flex items-center gap-3'>
          <Link to={backPath}>
            <Button variant='outline' size='icon' className='h-8 w-8 shrink-0'>
              <ChevronLeft className='h-5 w-5' />
            </Button>
          </Link>
          <div>
            <h1 className='text-xl font-bold md:text-2xl'>{title}</h1>
            {description && <p className='text-muted-foreground text-sm'>{description}</p>}
          </div>
        </div>
        <div className='flex items-center gap-2'>
          {updatedAt && (
            <p className='text-muted-foreground text-xs'>Updated at: {formatDateTime(updatedAt, locale, place)}</p>
          )}
          {onReload && (
            <Button variant='outline' size='icon' onClick={onReload} className='h-8 w-8 shrink-0'>
              <RefreshCw className='h-4 w-4' />
            </Button>
          )}
        </div>
      </div>
      <div className='min-h-0 flex-1'>{children}</div>
    </div>
  );
};

export default SchedulerMonitoringLayout;
