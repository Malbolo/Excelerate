// src/data/dummySchedules.ts
import { Schedule } from '@/types/scheduler';

export const dummySchedules: Schedule[] = [
  {
    scheduleId: 'sched-001',
    createdAt: new Date().toISOString(),
    title: 'Daily Data Processing Pipeline',
    description:
      'Processes daily sales data and updates the reporting dashboard.',
    userId: 'user-123',
    status: 'success', // Overall status of the last run or current state
    lastRunAt: new Date(Date.now() - 24 * 60 * 60 * 1000).toISOString(),
    nextRunAt: new Date(Date.now() + 24 * 60 * 60 * 1000).toISOString(),
    interval: { type: 'daily', time: '02:00' }, // Example for Daily interval
    jobList: [
      {
        jobId: 'job-001-a',
        title: 'Extract Data',
        description: 'Extract data from source databases.',
        createdAt: new Date().toISOString(),
        commandList: [
          {
            commandId: 'cmd-001',
            commandTitle: 'Connect to DB1',
            commandStatus: 'success',
          },
          {
            commandId: 'cmd-002',
            commandTitle: 'Run Extract Query',
            commandStatus: 'success',
          },
          {
            commandId: 'cmd-003',
            commandTitle: 'Save to Staging',
            commandStatus: 'success',
          },
        ],
      },
      {
        jobId: 'job-001-b',
        title: 'Transform Data',
        description: 'Clean and transform the extracted data.',
        createdAt: new Date().toISOString(),
        commandList: [
          {
            commandId: 'cmd-004',
            commandTitle: 'Load Staging Data',
            commandStatus: 'success',
          },
          {
            commandId: 'cmd-005',
            commandTitle: 'Apply Cleaning Rules',
            commandStatus: 'success',
          },
          {
            commandId: 'cmd-006',
            commandTitle: 'Aggregate Results',
            commandStatus: 'success',
          },
        ],
      },
      {
        jobId: 'job-001-c',
        title: 'Load Data',
        description: 'Load transformed data into the data warehouse.',
        createdAt: new Date().toISOString(),
        commandList: [
          {
            commandId: 'cmd-007',
            commandTitle: 'Connect to DWH',
            commandStatus: 'success',
          },
          {
            commandId: 'cmd-008',
            commandTitle: 'Execute Load Script',
            commandStatus: 'success',
          },
        ],
      },
    ],
  },
  {
    scheduleId: 'sched-002',
    createdAt: new Date().toISOString(),
    title: 'Weekly Report Generation',
    description: 'Generates the weekly financial summary report.',
    userId: 'user-456',
    status: 'error', // Example of a schedule with an error
    lastRunAt: new Date(Date.now() - 5 * 60 * 1000).toISOString(),
    nextRunAt: new Date(Date.now() + 7 * 24 * 60 * 60 * 1000).toISOString(),
    interval: { type: 'weekly', dayOfWeek: 'Mon', time: '09:00' }, // Example Weekly
    jobList: [
      {
        jobId: 'job-002-a',
        title: 'Fetch Financial Data',
        description: 'Get data from finance systems.',
        createdAt: new Date().toISOString(),
        commandList: [
          {
            commandId: 'cmd-009',
            commandTitle: 'API Call to Finance API',
            commandStatus: 'success',
          },
        ],
      },
      {
        jobId: 'job-002-b',
        title: 'Generate Report PDF',
        description: 'Create the PDF report document.',
        createdAt: new Date().toISOString(),
        commandList: [
          {
            commandId: 'cmd-010',
            commandTitle: 'Run Report Template',
            commandStatus: 'success',
          },
          {
            commandId: 'cmd-011',
            commandTitle: 'Render PDF',
            commandStatus: 'error',
          }, // Error here
          {
            commandId: 'cmd-012',
            commandTitle: 'Save PDF',
            commandStatus: 'pending',
          }, // Skipped due to error
        ],
      },
    ],
  },
  {
    scheduleId: 'sched-003',
    createdAt: new Date().toISOString(),
    title: 'Monthly Archiving',
    description: 'Archives old logs.',
    userId: 'user-123',
    status: 'pending', // Example of a pending/paused schedule
    lastRunAt: new Date(Date.now() - 30 * 24 * 60 * 60 * 1000).toISOString(),
    nextRunAt: new Date(Date.now() + 30 * 24 * 60 * 60 * 1000).toISOString(),
    interval: { type: 'monthly', dayOfMonth: 1, time: '00:00' }, // Example Monthly
    jobList: [
      {
        jobId: 'job-003-a',
        title: 'Archive Logs',
        description: 'Compress and move logs.',
        createdAt: new Date().toISOString(),
        commandList: [
          {
            commandId: 'cmd-013',
            commandTitle: 'Find Old Logs',
            commandStatus: 'pending',
          },
          {
            commandId: 'cmd-014',
            commandTitle: 'Compress Logs',
            commandStatus: 'pending',
          },
          {
            commandId: 'cmd-015',
            commandTitle: 'Move to Archive Storage',
            commandStatus: 'pending',
          },
        ],
      },
    ],
  },
];

// Define type for Interval if not already defined in types/scheduler
export type Daily = { type: 'Daily'; time: string };
export type Weekly = { type: 'Weekly'; dayOfWeek: string; time: string };
export type Monthly = { type: 'Monthly'; dayOfMonth: number; time: string };
export type Interval = Daily | Weekly | Monthly;
