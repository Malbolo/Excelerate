import { Suspense } from 'react';

import { createBrowserRouter } from 'react-router-dom';

import Layout from '@/components/Layout/Layout';
import MainPage from '@/pages';
import AgentMonitoringPage from '@/pages/agentMonitoring';
import JobAgentMonitoringPage from '@/pages/agentMonitoring/job';
import LoginPage from '@/pages/auth';
import CreateSchedulerPage from '@/pages/createScheduler';
import DaySchedulePage from '@/pages/daySchedulerMonitoring';
import JobManagementPage from '@/pages/jobManagement';
import MonthSchedulePage from '@/pages/monthSchedulerMonitoring';
import PlayGroundPage from '@/pages/playGround';
import ScheduleDetail from '@/pages/scheduleDetail';
import SchedulerManagementPage from '@/pages/schedulerManagement';

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
        path: 'scheduler-monitoring/day/:dayId',
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
    path: '/scheduler-monitoring/month/:monthId',
    element: (
      <Layout>
        <Suspense fallback={<div>로딩중...</div>}>
          <MonthSchedulePage />
        </Suspense>
      </Layout>
    ),
    name: 'SchedulerMonitoring',
  },
  {
    path: '/scheduler-monitoring/detail/:dayId/:scheduleId',
    element: (
      <Layout>
        <Suspense fallback={<div>로딩중...</div>}>
          <ScheduleDetail />
        </Suspense>
      </Layout>
    ),
    name: 'SchedulerMonitoring',
  },
  {
    path: '/scheduler-monitoring/create',
    element: (
      <Layout>
        <Suspense fallback={<div>로딩중...</div>}>
          <CreateSchedulerPage />
        </Suspense>
      </Layout>
    ),
    name: 'CreateScheduler',
  },
  {
    path: '/scheduler-management',
    element: (
      <Layout>
        <Suspense fallback={<div>로딩중...</div>}>
          <SchedulerManagementPage />
        </Suspense>
      </Layout>
    ),
    name: 'SchedulerList',
  },
  {
    path: '/scheduler-management/create',
    element: (
      <Layout>
        <Suspense fallback={<div>로딩중...</div>}>
          <CreateSchedulerPage />
        </Suspense>
      </Layout>
    ),
    name: 'CreateScheduler',
  },
  {
    path: '/agent-monitoring/job/:jobId',
    element: (
      <Layout>
        <Suspense fallback={<div>로딩중...</div>}>
          <JobAgentMonitoringPage />
        </Suspense>
      </Layout>
    ),
    name: 'JobAgentMonitoring',
  },
  {
    path: '/auth',
    element: (
      <Layout>
        <Suspense fallback={<div>로딩중...</div>}>
          <LoginPage />
        </Suspense>
      </Layout>
    ),
    name: 'Auth',
  },
];

const router = createBrowserRouter(routes);

export default router;
