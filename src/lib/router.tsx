import { Suspense } from 'react';

import { createBrowserRouter } from 'react-router-dom';

import MainPage from '@/pages';
import DaySchedulePage from '@/pages/daySchedulerMonitoring';
import ScheduleDetail from '@/pages/scheduleDetail';

import Layout from '../components/Layout/Layout';
import AgentMonitoringPage from '../pages/agentMonitoring';
import JobManagementPage from '../pages/jobManagement';
import SchedulerMonitoringPage from '../pages/monthSchedulerMonitoring';
import PlayGroundPage from '../pages/playGround';

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
    path: '/',
    children: [
      {
        path: 'scheduler-monitoring/:dayId',
        element: (
          <Layout>
            <Suspense fallback={<div>로딩중...</div>}>
              <DaySchedulePage />
            </Suspense>
          </Layout>
        ),
      },
    ],
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
  {
    path: '/scheduler-monitoring/:dayId/:scheduleId',
    element: (
      <Layout>
        <Suspense fallback={<div>로딩중...</div>}>
          <ScheduleDetail />
        </Suspense>
      </Layout>
    ),
    name: 'SchedulerMonitoring',
  },
];

const router = createBrowserRouter(routes);

export default router;
