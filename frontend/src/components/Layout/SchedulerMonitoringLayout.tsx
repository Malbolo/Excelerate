import { ArrowLeftIcon } from 'lucide-react';
import { useNavigate } from 'react-router-dom';

import { Button } from '@/components/ui/button';

interface SchedulerMonitoringLayoutProps {
  title: string;
  backPath: string;
  children: React.ReactNode;
}

const SchedulerMonitoringLayout = ({
  title,
  backPath,
  children,
}: SchedulerMonitoringLayoutProps) => {
  const navigate = useNavigate();

  const handleGoBack = () => {
    navigate(backPath);
  };

  return (
    <div className='container mx-auto h-full p-8'>
      <header className='mb-6 flex items-center gap-3 border-b border-gray-200 pb-4 md:gap-4'>
        {backPath !== '/' && (
          <Button
            variant='outline'
            size='icon'
            onClick={handleGoBack}
            aria-label='뒤로 가기'
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
