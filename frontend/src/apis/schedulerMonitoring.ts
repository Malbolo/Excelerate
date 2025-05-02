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

interface DayScheduleResponse {
  schedules: [
    {
      id: string;
      title: string;
      description: string;
      status: Status;
    },
  ];
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

const getDaySchedule = async (year: number, month: number, day: number) => {
  const { data } = await api<DayScheduleResponse[]>(
    `/api/schedules/statistics/daily?year=${year}&month=${month}&day=${day}`,
    { method: 'GET' },
  );

  if (!data) {
    // 에러바운더리로 캐치할 데이터
    throw new Error('No data');
  }

  return data;
};

const getMonthSchedule = async (year: number, month: number) => {
  const { data } = await api<GetMonthScheduleResponse[]>(
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
  year: number,
  month: number,
  day: number,
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

export const useGetDaySchedule = (year: number, month: number, day: number) => {
  return useSuspenseQuery({
    queryKey: ['daySchedule', year, month, day],
    queryFn: () => getDaySchedule(year, month, day),
  });
};

export const useGetMonthSchedule = (year: number, month: number) => {
  return useSuspenseQuery({
    queryKey: ['monthSchedule', year, month],
    queryFn: () => getMonthSchedule(year, month),
  });
};

export const useGetSchedule = (
  year: number,
  month: number,
  day: number,
  scheduleId: string,
) => {
  return useSuspenseQuery({
    queryKey: ['schedule', year, month, day, scheduleId],
    queryFn: () => getSchedule(year, month, day, scheduleId),
  });
};
