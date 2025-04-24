import { Suspense, lazy } from 'react';

import { createBrowserRouter } from 'react-router-dom';

import Layout from '../components/Layout/Layout';
import AgentMonitoringPage from '../pages/agentMonitoring';
import JobManagementPage from '../pages/jobManagement';
import PlayGroundPage from '../pages/playGround';
import SchedulerMonitoringPage from '../pages/schedulerMonitoring';

const MainPage = lazy(() => import('../pages'));

const routes = [
  {
    path: '/',
    element: (
      <Layout>
        <Suspense fallback={<div>로딩중...</div>}>
          <MainPage />
        </Suspense>
      </Layout>
    ),
    name: 'Main',
  },
  {
    path: '/agent-monitoring',
    element: (
      <Layout>
        <Suspense fallback={<div>로딩중...</div>}>
          <AgentMonitoringPage />
        </Suspense>
      </Layout>
    ),
    name: 'AgentMonitoring',
  },
  {
    path: '/job-management',
    element: (
      <Layout>
        <Suspense fallback={<div>로딩중...</div>}>
          <JobManagementPage />
        </Suspense>
      </Layout>
    ),
    name: 'JobManagement',
  },
  {
    path: '/playground',
    element: (
      <Layout>
        <Suspense fallback={<div>로딩중...</div>}>
          <PlayGroundPage />
        </Suspense>
      </Layout>
    ),
    name: 'PlayGround',
  },
  {
    path: '/scheduler-monitoring',
    element: (
      <Layout>
        <Suspense fallback={<div>로딩중...</div>}>
          <SchedulerMonitoringPage />
        </Suspense>
      </Layout>
    ),
    name: 'SchedulerMonitoring',
  },
];

const router = createBrowserRouter(routes);

export default router;
