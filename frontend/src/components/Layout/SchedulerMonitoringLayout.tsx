import { ArrowLeftIcon } from 'lucide-react';

import { Button } from '@/components/ui/button';
import useInternalRouter from '@/hooks/useInternalRouter';

interface SchedulerMonitoringLayoutProps {
  title: string;
  backPath: string;
  children: React.ReactNode;
  description?: string;
}

const SchedulerMonitoringLayout = ({ title, backPath, children, description }: SchedulerMonitoringLayoutProps) => {
  const { push } = useInternalRouter();

  return (
    <div className='bg-gradient container mx-auto h-screen overflow-y-hidden'>
      <header className='flex flex-col items-start gap-2 border-b p-6'>
        {backPath !== '/' && (
          <Button variant='ghost' size='sm' onClick={() => push(backPath)} className='flex items-center gap-2'>
            <ArrowLeftIcon className='h-4 w-4' />
            Back
          </Button>
        )}
        <div className='flex items-baseline gap-3 pl-3'>
          <h1 className='flex-1 text-lg font-bold'>{title}</h1>
          {description && <p className='text-accent-foreground truncate text-xs'>{description}</p>}
        </div>
      </header>
      <main>{children}</main>
    </div>
  );
};

export default SchedulerMonitoringLayout;
