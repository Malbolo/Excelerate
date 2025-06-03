import { Suspense } from 'react';

import { createBrowserRouter } from 'react-router-dom';

import ErrorBoundary from '@/components/Layout/ErrorBoundary';
import Layout from '@/components/Layout/Layout';
import Loading from '@/components/Layout/Loading';
import EditSchedulerPage from '@/pages/EditSchedulerPage';
import AgentMonitoringPage from '@/pages/agentMonitoring';
import LoginPage from '@/pages/auth';
import CreateSchedulerPage from '@/pages/createScheduler';
import DaySchedulePage from '@/pages/daySchedulerMonitoring';
import JobManagementPage from '@/pages/jobManagement';
import MainPage from '@/pages/main';
import MainJobEditPage from '@/pages/mainJobEdit';
import MonthSchedulePage from '@/pages/monthSchedulerMonitoring';
import PlayGroundPage from '@/pages/playGround';
import RagStudio from '@/pages/ragStudio';
import ScheduleDetail from '@/pages/scheduleDetail';
import SchedulerManagementPage from '@/pages/schedulerManagement';
import TemplateManagementPage from '@/pages/templateManagement';

const routes = [
  {
    path: '/',
    element: (
      <Layout>
        <Suspense fallback={<Loading />}>
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
        <Suspense fallback={<Loading />}>
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
        <Suspense fallback={<Loading />}>
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
        <Suspense fallback={<Loading />}>
          <PlayGroundPage />
        </Suspense>
      </Layout>
    ),
    errorElement: <ErrorBoundary />,
    name: 'PlayGround',
  },
  {
    path: '/rag-studio',
    element: (
      <Layout>
        <Suspense fallback={<Loading />}>
          <RagStudio />
        </Suspense>
      </Layout>
    ),
    errorElement: <ErrorBoundary />,
    name: 'RAGStudio',
  },
  {
    path: '/',
    children: [
      {
        path: 'scheduler-monitoring/day/:dayId',
        element: (
          <Layout>
            <Suspense fallback={<Loading />}>
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
        <Suspense fallback={<Loading />}>
          <MainJobEditPage />
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
        <Suspense fallback={<Loading />}>
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
        <Suspense fallback={<Loading />}>
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
        <Suspense fallback={<Loading />}>
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
        <Suspense fallback={<Loading />}>
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
        <Suspense fallback={<Loading />}>
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
        <Suspense fallback={<Loading />}>
          <EditSchedulerPage />
        </Suspense>
      </Layout>
    ),
    name: 'EditScheduler',
  },
  {
    path: '/auth',
    element: (
      <Layout>
        <Suspense fallback={<Loading />}>
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
        <Suspense fallback={<Loading />}>
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
