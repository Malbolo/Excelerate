import { useSuspenseQuery } from '@tanstack/react-query';

import { Status } from '@/types/scheduler';

import { api } from './core';

interface GetMonthScheduleResponse {
  statistics: [
    {
      day: number;
      pending: number;
      success: number;
      fail: number;
    },
  ];
}

export interface DaySchedule {
  id: string;
  title: string;
  description: string;
  status: Status;
}

interface DayScheduleResponse {
  schedules: DaySchedule[];
}

interface ScheduleResponse {
  id: string;
  title: string;
  description: string;
  created_at: string;
  userId: string;
  status: Status;
  jobs: [
    {
      id: string;
      name: string;
      order: number;
      commands: [
        {
          content: string;
          status: Status;
          order: number;
        },
      ];
    },
  ];
}

const getDaySchedules = async (year: string, month: string, day: string) => {
  const { data } = await api<DayScheduleResponse>(
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

const getSchedule = async (
  year: string,
  month: string,
  day: string,
  scheduleId: string,
) => {
  const { data } = await api<ScheduleResponse>(
    `/api/schedules/${scheduleId}?year=${year}&month=${month}&day=${day}`,
    { method: 'GET' },
  );

  if (!data) {
    // 에러바운더리로 캐치할 데이터
    throw new Error('No data');
  }

  return data;
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

export const useGetSchedule = (
  year: string,
  month: string,
  day: string,
  scheduleId: string,
) => {
  return useSuspenseQuery({
    queryKey: ['schedule', year, month, day, scheduleId],
    queryFn: () => getSchedule(year, month, day, scheduleId),
  });
};
