import { Suspense } from 'react';

import { createBrowserRouter } from 'react-router-dom';

import ErrorBoundary from '@/components/Layout/ErrorBoundary';
import Layout from '@/components/Layout/Layout';
import EditSchedulerPage from '@/pages/EditSchedulerPage';
import AgentMonitoringPage from '@/pages/agentMonitoring';
import JobAgentMonitoringPage from '@/pages/agentMonitoring/job';
import LoginPage from '@/pages/auth';
import CreateSchedulerPage from '@/pages/createScheduler';
import DaySchedulePage from '@/pages/daySchedulerMonitoring';
import JobManagementPage from '@/pages/jobManagement';
import JobEditPage from '@/pages/jobManagement/edit';
import MainPage from '@/pages/main';
import MonthSchedulePage from '@/pages/monthSchedulerMonitoring';
import PlayGroundPage from '@/pages/playGround';
import ScheduleDetail from '@/pages/scheduleDetail';
import SchedulerManagementPage from '@/pages/schedulerManagement';
import TemplateManagementPage from '@/pages/templateManagement';

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
    errorElement: <ErrorBoundary />,
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
    errorElement: <ErrorBoundary />,
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
    errorElement: <ErrorBoundary />,
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
    errorElement: <ErrorBoundary />,
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
        errorElement: <ErrorBoundary />,
      },
    ],
  },
  {
    path: '/job-management/edit/:jobId',
    element: (
      <Layout>
        <Suspense fallback={<div>로딩중...</div>}>
          <JobEditPage />
        </Suspense>
      </Layout>
    ),
    errorElement: <ErrorBoundary />,
    name: 'JobEdit',
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
    errorElement: <ErrorBoundary />,
    name: 'SchedulerMonitoring',
  },
  {
    path: '/scheduler-monitoring/detail/:dayId/:scheduleId/:runId',
    element: (
      <Layout>
        <Suspense fallback={<div>로딩중...</div>}>
          <ScheduleDetail />
        </Suspense>
      </Layout>
    ),
    errorElement: <ErrorBoundary />,
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
    errorElement: <ErrorBoundary />,
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
    errorElement: <ErrorBoundary />,
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
    errorElement: <ErrorBoundary />,
    name: 'CreateScheduler',
  },
  {
    path: '/scheduler-management/edit/:scheduleId',
    element: (
      <Layout>
        <Suspense fallback={<div>로딩중...</div>}>
          <EditSchedulerPage />
        </Suspense>
      </Layout>
    ),
    name: 'EditScheduler',
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
    errorElement: <ErrorBoundary />,
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
    errorElement: <ErrorBoundary />,
    name: 'Auth',
  },
  {
    path: '/template-management',
    element: (
      <Layout>
        <Suspense fallback={<div>로딩중...</div>}>
          <TemplateManagementPage />
        </Suspense>
      </Layout>
    ),
    errorElement: <ErrorBoundary />,
    name: 'TemplateManagement',
  },
];

const router = createBrowserRouter(routes);

export default router;
