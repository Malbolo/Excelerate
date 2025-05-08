import { useSuspenseQuery } from '@tanstack/react-query';

import { Status } from '@/types/scheduler';

import { api } from './core';

interface MonthSchedule {
  date: string;
  pending: number;
  success: number;
  failed: number;
}

type GetMonthScheduleResponse = MonthSchedule[];

export interface DaySchedule {
  schedule_id: string;
  description: string;
  run_id: string;
  title: string;
  owner: string;
  status: Status;
  start_time: string;
  end_time: string;
}

interface GetDayScheduleResponse {
  date: string;
  success: DaySchedule[];
  failed: DaySchedule[];
  pending: DaySchedule[];
}

interface GetRunIdResponse {
  schedule_id: string;
  title: string;
  run_id: string;
  status: string;
  start_time: string;
  end_time: string;
  duration: number;
  conf: object;
  jobs: [
    {
      job_id: string;
      status: string;
      start_time: string;
      end_time: string;
      duration: number;
      logs_url: string;
    },
  ];
}

interface Command {
  content: string;
  order: number;
}

export interface Job {
  commands: Command[];
  description: string;
  end_time: string;
  id: string;
  logs_url: string;
  start_time: string;
  status: 'failed' | 'success' | 'pending';
  title: string;
}

export interface RunDetailResponse {
  schedule_id: string;
  title: string;
  run_id: string;
  status: string;
  start_time: string;
  end_time: string;
  jobs: Job[];
  logs_url: string;
}

const getRunDetail = async (scheduleId: string, runId: string) => {
  const { error, success, data } = await api<RunDetailResponse>(
    `/api/schedules/${scheduleId}/runs/${runId}`,
  );

  if (!success) {
    throw new Error(error);
  }

  return data;
};

const getDaySchedules = async (year: string, month: string, day: string) => {
  const { data } = await api<GetDayScheduleResponse>(
    `/api/schedules/statistics/daily?year=${year}&month=${month}&day=${day}`,
    { method: 'GET' },
  );

  if (!data) {
    // 에러바운더리로 캐치할 데이터
    throw new Error('No data');
  }

  return data;
};

const getMonthSchedules = async (year: string, month: string) => {
  const { data } = await api<GetMonthScheduleResponse>(
    `/api/schedules/statistics/monthly?year=${year}&month=${month}`,
    { method: 'GET' },
  );

  if (!data) {
    // 에러바운더리로 캐치할 데이터
    throw new Error('No data');
  }

  return data;
};

const getSchedule = async (schedule_id: string, run_id: string) => {
  const { data } = await api<GetRunIdResponse>(
    `/api/schedules/${schedule_id}/runs/${run_id}`,
    { method: 'GET' },
  );

  if (!data) {
    // 에러바운더리로 캐치할 데이터
    throw new Error('No data');
  }

  return data;
};

export const useGetRunDetail = (scheduleId: string, runId: string) => {
  return useSuspenseQuery({
    queryKey: ['scheduleDetail', scheduleId, runId],
    queryFn: () => getRunDetail(scheduleId, runId),
  });
};

export const useGetDaySchedules = (
  year: string,
  month: string,
  day: string,
) => {
  return useSuspenseQuery({
    queryKey: ['daySchedules', year, month, day],
    queryFn: () => getDaySchedules(year, month, day),
  });
};

export const useGetMonthSchedules = (year: string, month: string) => {
  return useSuspenseQuery({
    queryKey: ['monthSchedules', year, month],
    queryFn: () => getMonthSchedules(year, month),
  });
};

export const useGetSchedule = (schedule_id: string, run_id: string) => {
  return useSuspenseQuery({
    queryKey: ['schedule', schedule_id, run_id],
    queryFn: () => getSchedule(schedule_id, run_id),
  });
};
