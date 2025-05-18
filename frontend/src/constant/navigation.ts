const ADMIN_NAV_ITEMS = [
  { label: 'Main', to: '/' },
  { label: 'Job Management', to: '/job-management' },
  { label: 'Scheduler Management', to: '/scheduler-management' },
  {
    label: 'Scheduler Monitoring',
    to: `/scheduler-monitoring/month/${new Date().getFullYear()}-${String(new Date().getMonth() + 1).padStart(2, '0')}`,
    basePath: '/scheduler-monitoring',
  },
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

export { ADMIN_NAV_ITEMS, USER_NAV_ITEMS };
