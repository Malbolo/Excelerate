import cn from 'clsx';
import { Link } from 'react-router-dom';

const navItems = [
  { label: 'Main', to: '/' },
  { label: 'Job Management', to: '/job-management' },
  { label: 'Scheduler Monitoring', to: '/scheduler-monitoring' },
  { label: 'Agent Monitoring', to: '/agent-monitoring' },
  { label: 'Play Ground', to: '/playground' },
];

const NavigationBar: React.FC = () => {
  return (
    <nav className='flex h-full w-60 flex-col bg-[#F5F5F5] py-6'>
      <div className='mt-9 mb-15 text-center text-2xl'>Samsung</div>
      <ul className='flex flex-col'>
        {navItems.map(({ label, to }) => {
          const isActive =
            to === '/'
              ? location.pathname === '/'
              : location.pathname.startsWith(to);

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
    </nav>
  );
};

export default NavigationBar;
