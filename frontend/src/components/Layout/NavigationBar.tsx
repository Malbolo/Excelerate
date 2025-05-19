import { Workflow } from 'lucide-react';
import { Link, useLocation } from 'react-router-dom';

import { useGetUserInfoAPI } from '@/apis/auth';
import logo from '@/assets/images/logo.png';
import { Button } from '@/components/ui/button';
import { ADMIN_NAV_ITEMS, GUEST_NAV_ITEMS, USER_NAV_ITEMS } from '@/constant/navigation';
import { cn } from '@/lib/utils';

import LocaleSelector from './LocaleSelector';
import LogoutButton from './LogoutButton';

const NavigationBar = () => {
  const { data: userInfo } = useGetUserInfoAPI();
  const { name, role } = userInfo || { role: 'GUEST', name: '' };
  const navMenu = role === 'ADMIN' ? ADMIN_NAV_ITEMS : role === 'GUEST' ? GUEST_NAV_ITEMS : USER_NAV_ITEMS;
  const location = useLocation();

  return (
    <nav className='flex h-full min-w-66 shrink-0 flex-col border-r bg-[#FAFCFF] pt-6 pb-2'>
      <div className='mt-10 mb-9 flex flex-col items-center justify-center gap-3'>
        <img src={logo} alt='Samsung Logo' width={150} height={23} />
        <div className='flex items-center gap-1'>
          <Workflow className='h-3 w-3' />
          <p className='text-xs'>GenAI Report Automation</p>
        </div>
      </div>

      <ul className='flex grow flex-col gap-2 p-4'>
        {navMenu.map(({ label, to, basePath }) => {
          let isActive;
          if (label === 'Scheduler Monitoring') {
            isActive = location.pathname.startsWith(basePath || '/scheduler-monitoring');
          } else {
            isActive = to === '/' ? location.pathname === '/' : location.pathname.startsWith(to);
          }

          return (
            <Link key={to} to={to}>
              <li
                className={cn(
                  'hover:text-accent-foreground flex items-center rounded-lg px-4 py-4 font-bold transition-all hover:bg-[#F0F7FF]',
                  isActive && 'box-shadow border-primary/70 text-accent-foreground border bg-[#F0F7FF]',
                )}
              >
                {label}
              </li>
            </Link>
          );
        })}
      </ul>

      <div className='mt-auto flex flex-col gap-2 border-t p-4'>
        {name ? (
          <LogoutButton name={name} />
        ) : (
          <Link to='/auth' className='w-full'>
            <Button variant='default' className='w-full'>
              Login
            </Button>
          </Link>
        )}
        <LocaleSelector />
      </div>
    </nav>
  );
};

export default NavigationBar;
