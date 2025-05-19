import { useState } from 'react';

import { ChevronsLeft, ChevronsRight, SquareChartGantt } from 'lucide-react';
import { Link, useLocation } from 'react-router-dom';

import { useGetUserInfoAPI } from '@/apis/auth';
import logo from '@/assets/images/logo.png';
import { Button } from '@/components/ui/button';
import { ADMIN_NAV_ITEMS, GUEST_NAV_ITEMS, USER_NAV_ITEMS } from '@/constant/navigation';
import { cn } from '@/lib/utils';

import LocaleSelector from './LocaleSelector';
import LogoutButton from './LogoutButton';

const NavigationBar = () => {
  const [isCollapsed, setIsCollapsed] = useState(false);
  const { data: userInfo } = useGetUserInfoAPI();
  const { name, role } = userInfo || { role: 'GUEST', name: '' };
  const navMenu = role === 'ADMIN' ? ADMIN_NAV_ITEMS : role === 'GUEST' ? GUEST_NAV_ITEMS : USER_NAV_ITEMS;
  const location = useLocation();

  const toggleCollapse = () => setIsCollapsed(!isCollapsed);

  return (
    <nav
      className={cn(
        'relative flex h-full shrink-0 flex-col border-r bg-[#FAFCFF] pt-6 pb-2 transition-all duration-300 ease-in-out',
        isCollapsed ? 'w-20' : 'min-w-66',
      )}
    >
      <Button
        variant='ghost'
        size='icon'
        className='absolute top-3 right-3 z-10 rounded-md p-1'
        onClick={toggleCollapse}
        title={isCollapsed ? 'Expand' : 'Collapse'}
      >
        {isCollapsed ? <ChevronsRight className='h-5 w-5' /> : <ChevronsLeft className='h-5 w-5' />}
      </Button>

      <div className='mt-10 mb-9 flex flex-col items-center justify-center gap-3 px-4'>
        <img src={logo} alt='Samsung Logo' width={isCollapsed ? 40 : 150} height={isCollapsed ? 6 : 23} />
        {!isCollapsed && (
          <div className='flex items-center gap-1'>
            <SquareChartGantt className='h-3 w-3' />
            <p className='text-center text-xs'>GenAI Report Automation</p>
          </div>
        )}
      </div>

      <ul className='flex grow flex-col gap-2 p-4 pt-0'>
        {navMenu.map(({ label, to, basePath, icon: Icon }) => {
          let isActive;
          if (label === 'Scheduler Monitoring') {
            isActive = location.pathname.startsWith(basePath || '/scheduler-monitoring');
          } else {
            isActive = to === '/' ? location.pathname === '/' : location.pathname.startsWith(to);
          }

          return (
            <Link key={to} to={to} title={isCollapsed ? label : undefined}>
              <li
                className={cn(
                  'hover:text-accent-foreground flex items-center rounded-lg px-3 py-4 font-bold transition-all hover:bg-[#F0F7FF]',
                  isActive && 'box-shadow border-primary/70 text-accent-foreground border bg-[#F0F7FF]',
                  isCollapsed ? 'justify-center py-3' : 'justify-start gap-3',
                )}
              >
                {Icon && <Icon className={cn('h-5 w-5', isCollapsed ? 'mx-auto' : '')} />}
                {!isCollapsed && <span className='truncate'>{label}</span>}
              </li>
            </Link>
          );
        })}
      </ul>

      <div className={cn('mt-auto flex flex-col gap-2 border-t p-4', isCollapsed && 'items-center')}>
        {name ? (
          <LogoutButton name={name} isCollapsed={isCollapsed} />
        ) : (
          <Link to='/auth' className='w-full'>
            <Button variant='default' className={cn('w-full', isCollapsed && 'px-2')}>
              {isCollapsed ? <ChevronsRight className='h-5 w-5' /> : 'Login'}
            </Button>
          </Link>
        )}
        {!isCollapsed && <LocaleSelector />}
      </div>
    </nav>
  );
};

export default NavigationBar;
