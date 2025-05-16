import { ArrowLeftIcon } from 'lucide-react';

import { Button } from '@/components/ui/button';
import useInternalRouter from '@/hooks/useInternalRouter';

interface SchedulerMonitoringLayoutProps {
  title: string;
  backPath: string;
  children: React.ReactNode;
}

const SchedulerMonitoringLayout = ({ title, backPath, children }: SchedulerMonitoringLayoutProps) => {
  const { push } = useInternalRouter();

  const handleGoBack = () => {
    push(backPath);
  };

  return (
    <div className='container mx-auto h-full p-8'>
      <header className='mb-6 flex items-center gap-3 border-b border-gray-200 pb-4 md:gap-4'>
        {backPath !== '/' && (
          <Button
            variant='outline'
            size='icon'
            onClick={handleGoBack}
            aria-label='back'
            className='h-9 w-9 flex-shrink-0'
          >
            <ArrowLeftIcon className='h-5 w-5' />
          </Button>
        )}
        <h1 className='flex-1 text-xl font-bold text-gray-800'>{title}</h1>
      </header>
      <main>{children}</main>
    </div>
  );
};

export default SchedulerMonitoringLayout;
