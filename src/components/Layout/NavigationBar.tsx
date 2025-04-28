import cn from 'clsx';
import { Link, useLocation } from 'react-router-dom';

const navItems = [
  { label: 'Main', to: '/' },
  { label: 'Job Management', to: '/job-management' },
  {
    label: 'Scheduler Monitoring',
    to: `/scheduler-monitoring/month/${new Date().getFullYear()}-${String(new Date().getMonth() + 1).padStart(2, '0')}`, // 월을 두 자리로 (예: 2025-04)
    basePath: '/scheduler-monitoring',
  },
  { label: 'Agent Monitoring', to: '/agent-monitoring' },
  { label: 'Play Ground', to: '/playground' },
];

const NavigationBar: React.FC = () => {
  const location = useLocation();

  return (
    <nav className='flex h-full w-60 flex-col bg-[#F5F5F5] py-6'>
      <div className='mt-9 mb-15 text-center text-2xl'>Samsung</div>
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
                  'block w-full p-6 text-[20px] font-bold',
                  isActive && 'bg-[#034EA2] text-[#ffffff]',
                )}
              >
                {label}
              </li>
            </Link>
          );
        })}
      </ul>
      {/* <div className='flex w-full justify-center'>
        <LanguageSelector />
      </div> */}
    </nav>
  );
};

export default NavigationBar;
