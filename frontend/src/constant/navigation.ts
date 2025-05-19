import { Briefcase, CalendarClock, Home, MonitorPlay, Play, Workflow } from 'lucide-react';

const ADMIN_NAV_ITEMS = [
  { label: 'Main', to: '/', icon: Home },
  { label: 'Job Management', to: '/job-management', icon: Briefcase },
  { label: 'Scheduler Management', to: '/scheduler-management', icon: CalendarClock },
  {
    label: 'Scheduler Monitoring',
    to: `/scheduler-monitoring/month/${new Date().getFullYear()}-${String(new Date().getMonth() + 1).padStart(2, '0')}`,
    basePath: '/scheduler-monitoring',
    icon: MonitorPlay,
  },
  { label: 'Agent Monitoring', to: '/agent-monitoring', icon: Workflow },
  { label: 'Play Ground', to: '/playground', icon: Play },
];

const USER_NAV_ITEMS = [
  { label: 'Main', to: '/', icon: Home },
  {
    label: 'Job Management',
    to: '/job-management',
    basePath: '/job-management',
    icon: Briefcase,
  },
  { label: 'Play Ground', to: '/playground', icon: Play },
];

const GUEST_NAV_ITEMS = [
  { label: 'Main', to: '/', basePath: '/', icon: Home },
  { label: 'Play Ground', to: '/playground', basePath: '/playground', icon: Play },
];

export { ADMIN_NAV_ITEMS, GUEST_NAV_ITEMS, USER_NAV_ITEMS };
