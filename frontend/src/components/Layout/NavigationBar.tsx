import { useQueryClient } from '@tanstack/react-query';
import { Link, useLocation } from 'react-router-dom';
import { toast } from 'sonner';

import { useGetUserInfoAPI } from '@/apis/auth';
import logo from '@/assets/images/logo.png';
import { Button } from '@/components/ui/button';
import useInternalRouter from '@/hooks/useInternalRouter';
import { cn } from '@/lib/utils';

const ADMIN_NAV_ITEMS = [
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

const USER_NAV_ITEMS = [
  { label: 'Main', to: '/' },
  {
    label: 'Job Management',
    to: '/job-management',
    basePath: '/job-management',
  },
  { label: 'Play Ground', to: '/playground' },
];

const NavigationBar = () => {
  const { data: userInfo } = useGetUserInfoAPI();
  const queryClient = useQueryClient();
  const { replace } = useInternalRouter();

  const { name, role } = userInfo || {};
  const navMenu = role === 'ADMIN' ? ADMIN_NAV_ITEMS : USER_NAV_ITEMS;

  const location = useLocation();

  const handleLogoutClick = () => {
    localStorage.removeItem('token');
    toast.success('Logout completed successfully.');
    queryClient.resetQueries();
    replace('/');
  };

  return (
    <nav className='flex h-full min-w-66 shrink-0 flex-col border-r bg-[#F5F5F5] pt-6 pb-2'>
      <div className='mt-9 mb-15 flex justify-center'>
        <img src={logo} alt='Samsung Logo' width={150} height={23} />
      </div>

      <ul className='flex grow flex-col'>
        {navMenu.map(({ label, to, basePath }) => {
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
                  'block w-full px-4 py-6 text-[20px] font-bold transition-colors duration-150 ease-in-out hover:bg-gray-200',
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

      <div className='mt-auto border-gray-300 p-4'>
        {name ? (
          <div className='flex flex-col items-center gap-3'>
            <span className='text-sm text-gray-800'>Hello, {name}!</span>
            <Button
              variant='outline'
              size='sm'
              className='w-full'
              onClick={handleLogoutClick}
            >
              Logout
            </Button>
          </div>
        ) : (
          <Link to='/auth' className='w-full'>
            <Button variant='default' className='w-full'>
              Login
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
