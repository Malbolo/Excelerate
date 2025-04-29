import { useMutation, useQuery } from '@tanstack/react-query';
import { toast } from 'sonner';

import { CreateScheduleFormData } from '@/pages/createScheduler/components/CreateScheduleModal';
import { Schedule, Status } from '@/types/scheduler';

import { api } from './core';

interface DailySchedule {
  status: Status;
  scheduleList: Schedule[];
}

interface GetMonthScheduleResponse {
  schedules: DailySchedule[];
}

interface CreateScheduleResponse {
  message: string;
}

const getMonthSchedule = async (year: number, month: number) => {
  const { data } = await api<GetMonthScheduleResponse[]>(
    `/schedule/month?year=${year}&month=${month}`,
    { method: 'GET' },
  );

  if (!data) {
    // 에러바운더리로 캐치할 데이터
    throw new Error('No data');
  }

  return data;
};

const createSchedule = async (schedule: CreateScheduleFormData) => {
  const { data, error, success } = await api<CreateScheduleResponse>(
    '/schedule',
    {
      method: 'POST',
      body: JSON.stringify(schedule),
    },
  );

  if (!success) {
    throw new Error(error);
  }

  return data;
};

export const useGetMonthSchedule = (year: number, month: number) => {
  return useQuery({
    queryKey: ['monthSchedule', year, month],
    queryFn: () => getMonthSchedule(year, month),
  });
};

export const useCreateSchedule = () => {
  const { mutate } = useMutation({
    mutationFn: (schedule: CreateScheduleFormData) => createSchedule(schedule),
    onSuccess: data => {
      toast.success(data.message);
    },
    // post에서는 에러 바운더리로 캐치가 안되서 추가
    onError: error => {
      toast.error(error.message);
    },
  });

  return mutate;
};
