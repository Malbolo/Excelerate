import { useQueryClient } from '@tanstack/react-query';
import { Link, useLocation, useNavigate } from 'react-router-dom';
import { toast } from 'sonner';

import { useGetUserInfoAPI } from '@/apis/auth';
import { Button } from '@/components/ui/button';
import { cn } from '@/lib/utils';

const navItems = [
  { label: 'Main', to: '/' },
  { label: 'Job Management', to: '/job-management' },
  {
    label: 'Scheduler Monitoring',
    to: `/scheduler-monitoring/month/${new Date().getFullYear()}-${String(new Date().getMonth() + 1).padStart(2, '0')}`,
    basePath: '/scheduler-monitoring',
  },
  { label: 'Scheduler Management', to: '/scheduler-management' },
  { label: 'Agent Monitoring', to: '/agent-monitoring' },
  { label: 'Play Ground', to: '/playground' },
];

const NavigationBar = () => {
  // 닉네임은 추후에 실제 데이터를 사용할 예정
  const { data: userInfo } = useGetUserInfoAPI();
  const queryClient = useQueryClient();
  const navigate = useNavigate();

  const { name } = userInfo || {};

  const location = useLocation();

  const handleLogoutClick = () => {
    localStorage.removeItem('token');
    toast.success('로그아웃이 완료되었습니다.');
    queryClient.invalidateQueries({ queryKey: ['userInfo'] });
    navigate('/');
  };

  return (
    <nav className='flex h-full w-60 flex-col bg-[#F5F5F5] py-6'>
      <div className='mt-9 mb-15 text-center text-2xl'>Samsung</div>

      {/* 네비게이션 링크 (기존과 동일) */}
      <ul className='flex grow flex-col'>
        {navItems.map(({ label, to, basePath }) => {
          let isActive;
          if (label === 'Scheduler Monitoring') {
            isActive = location.pathname.startsWith(
              basePath || '/scheduler-monitoring',
            );
          } else {
            isActive =
              to === '/'
                ? location.pathname === '/'
                : location.pathname.startsWith(to);
          }

          return (
            <Link key={to} to={to}>
              <li
                className={cn(
                  'block w-full p-6 text-[20px] font-bold transition-colors duration-150 ease-in-out hover:bg-gray-200', // 호버 효과 추가 (선택 사항)
                  isActive
                    ? 'bg-[#034EA2] text-[#ffffff] hover:bg-[#023a81]'
                    : 'text-gray-700',
                )}
              >
                {label}
              </li>
            </Link>
          );
        })}
      </ul>

      <div className='mt-auto border-t border-gray-300 p-4'>
        {name ? (
          <div className='flex flex-col items-center gap-3'>
            <span className='text-sm font-medium text-gray-800'>
              안녕하세요, {name}님!
            </span>
            <Button
              variant='outline'
              size='sm'
              className='w-full'
              onClick={handleLogoutClick}
            >
              로그아웃
            </Button>
          </div>
        ) : (
          <Link to='/auth' className='w-full'>
            <Button variant='default' className='w-full'>
              로그인하러 가기
            </Button>
          </Link>
        )}
      </div>
      {/* <div className='flex w-full justify-center'>
        <LanguageSelector />
      </div> */}
    </nav>
  );
};

export default NavigationBar;
