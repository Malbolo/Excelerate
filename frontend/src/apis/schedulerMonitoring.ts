import { useSuspenseQuery } from '@tanstack/react-query';

import { Status } from '@/types/job';

import { api } from './core';
import { Job } from './jobManagement';

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

export interface JobSchedule extends Job {
  end_time: string;
  logs_url: string;
  start_time: string;
  status: Status;
  error_log: JobError | null;
}

export interface RunDetailResponse {
  schedule_id: string;
  title: string;
  run_id: string;
  status: string;
  start_time: string;
  end_time: string;
  jobs: JobSchedule[];
  logs_url: string;
}

export interface JobError {
  error_time: string;
  error_message: string;
  error_type?: string;
  error_trace?: string;
}

// runId 실행된 스케쥴 상세 조회
const getRunDetail = async (scheduleId: string, runId: string) => {
  const { error, success, data } = await api<RunDetailResponse>(`/api/schedules/${scheduleId}/runs/${runId}`);

  if (!success) {
    throw new Error(error);
  }

  return data;
};

// 일별 스케쥴 조회
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

// 월별 스케쥴 조회
const getMonthSchedules = async (year: string, month: string) => {
  const { data } = await api<GetMonthScheduleResponse>(
    `/api/schedules/statistics/monthly?year=${year}&month=${month}`,
    { method: 'GET' },
  );

  if (!data) {
    throw new Error('No data');
  }

  return data;
};

// runId 실행된 스케쥴 상세 조회 hook - tasntack/query
export const useGetRunDetail = (scheduleId: string, runId: string) => {
  return useSuspenseQuery({
    queryKey: ['runDetail', scheduleId, runId],
    queryFn: () => getRunDetail(scheduleId, runId),
  });
};

// 일별 스케쥴 조회 hook - tasntack/query
export const useGetDaySchedules = (year: string, month: string, day: string) => {
  return useSuspenseQuery({
    queryKey: ['daySchedules', year, month, day],
    queryFn: () => getDaySchedules(year, month, day),
  });
};

// 월별 스케쥴 조회 hook - tasntack/query
export const useGetMonthSchedules = (year: string, month: string) => {
  return useSuspenseQuery({
    queryKey: ['monthSchedules', year, month],
    queryFn: () => getMonthSchedules(year, month),
  });
};
