// src/layouts/SchedulerMonitoringLayout.tsx (또는 원하는 경로)
import React from 'react';

import { ArrowLeftIcon } from 'lucide-react';
import { useNavigate } from 'react-router-dom';

// 뒤로가기 아이콘
import { Button } from '@/components/ui/button';

// shadcn/ui 버튼 사용 가정

interface SchedulerMonitoringLayoutProps {
  /** 페이지 상단에 표시될 제목 */
  title: string;
  /** 뒤로가기 버튼 클릭 시 이동할 경로 */
  backPath: string;
  /** 레이아웃 내부에 렌더링될 페이지 컨텐츠 */
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
    <div className='relative container mx-auto h-full'>
      <header className='mb-6 flex items-center gap-3 border-b border-gray-200 pb-4 md:mb-8 md:gap-4'>
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
        <h1 className='flex-1 text-xl font-bold text-gray-800 md:text-2xl'>
          {title}
        </h1>
      </header>
      <main>{children}</main>
    </div>
  );
};

export default SchedulerMonitoringLayout;
