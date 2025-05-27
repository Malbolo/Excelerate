import { useMutation, useQueryClient, useSuspenseQuery } from '@tanstack/react-query';
import { toast } from 'sonner';

import useInternalRouter from '@/hooks/useInternalRouter';

import { api } from './core';
import { Job } from './jobManagement';

export interface FrequencyDisplay {
  type: string;
  time: string;
  dayOfWeek?: string;
  dayOfMonth?: number;
}

export interface Schedule {
  schedule_id: string;
  title: string;
  description: string;
  frequency: 'daily' | 'weekly' | 'monthly';
  frequency_cron: string;
  frequency_display: FrequencyDisplay;
  owner: string;
  is_paused: boolean;
  created_at: string;
  updated_at: string | null;
  start_date: string;
  end_date: string;
  execution_time: string;
  success_emails: string[];
  failure_emails: string[];
  jobs:
    | {
        id: string;
        order: number;
      }[]
    | Job[];
  last_run: null | {
    end_time: string;
    status: 'success' | 'failed';
  };
  next_run: null | {
    scheduled_time: string;
  };
}

interface ScheduleListResponse {
  schedules: Schedule[];
  total_pages: number;
}

interface CreateScheduleRequest {
  schedule: string;
}

interface EditScheduleRequest {
  schedule: string;
  scheduleId: string;
}

interface ScheduleParams {
  page?: string;
  size?: string;
  title?: string;
  owner?: string;
  frequency?: string;
  status?: string;
}

// 스케쥴 상세 조회 - 수정페이지에서 초기 데이터 로드할 때 필요
const getScheduleDetail = async (scheduleId: string) => {
  const { error, success, data } = await api<Schedule>(`/api/schedules/${scheduleId}`);

  if (!success) {
    throw new Error(error);
  }

  return data;
};

// 스케쥴 목록 조회
const getScheduleList = async ({
  page = '1',
  size = '10',
  title = '',
  owner = '',
  frequency = '',
  status = '',
}: ScheduleParams) => {
  const searchParams = new URLSearchParams();

  Object.entries({ page, size, title, owner, frequency, status }).forEach(([key, value]) => {
    if (value) {
      searchParams.set(key, value);
    }
  });

  const { error, success, data } = await api<ScheduleListResponse>(`/api/schedules?${searchParams.toString()}`);

  if (!success) {
    throw new Error(error);
  }

  return data;
};

// 스케쥴 생성
const createSchedule = async ({ schedule }: CreateScheduleRequest) => {
  const { error, success } = await api('/api/schedules', {
    method: 'POST',
    body: schedule,
  });

  if (!success) {
    throw new Error(error);
  }

  return;
};

// 스케쥴 수정
const updateSchedule = async ({ scheduleId, schedule }: EditScheduleRequest) => {
  const { error, success } = await api(`/api/schedules/${scheduleId}`, {
    method: 'PATCH',
    body: schedule,
  });

  if (!success) {
    throw new Error(error);
  }

  return;
};

// 스케쥴 활성화/비활성화
const toggleSchedule = async (scheduleId: string) => {
  const { error, success } = await api(`/api/schedules/${scheduleId}/toggle`, {
    method: 'PATCH',
  });

  if (!success) {
    throw new Error(error);
  }

  return;
};

// 스케쥴 일회성 실행
const oneTimeSchedule = async (scheduleId: string) => {
  const { error, success } = await api(`/api/schedules/${scheduleId}/start`, {
    method: 'POST',
  });

  if (!success) {
    throw new Error(error);
  }

  return;
};

// 스케쥴 삭제
const deleteSchedule = async (scheduleId: string) => {
  const { error, success } = await api(`/api/schedules/${scheduleId}`, {
    method: 'DELETE',
  });

  if (!success) {
    throw new Error(error);
  }

  return;
};

// 스케쥴 목록 조회 hook - tasntack/query
export const useGetScheduleList = ({ page, size, title, owner, frequency, status }: ScheduleParams) => {
  return useSuspenseQuery({
    queryKey: ['scheduleList', page, size, title, owner, frequency, status],
    queryFn: () => getScheduleList({ page, size, title, owner, frequency, status }),
  });
};

// 스케쥴 상세 조회 hook - tasntack/query
export const useGetScheduleDetail = (scheduleId: string) => {
  return useSuspenseQuery({
    queryKey: ['scheduleDetail', scheduleId],
    queryFn: () => getScheduleDetail(scheduleId),
  });
};

// 스케쥴 활성화/비활성화 hook - tasntack/mutation
export const useToggleSchedule = () => {
  const queryClient = useQueryClient();
  const { mutate } = useMutation({
    mutationFn: (scheduleId: string) => toggleSchedule(scheduleId),
    onSuccess: () => {
      toast.success('Schedule toggled successfully');
      queryClient.invalidateQueries({ queryKey: ['scheduleList'] });
    },
    onError: error => {
      toast.error(error.message);
    },
  });

  return mutate;
};

// 스케쥴 일회성 실행 hook - tasntack/mutation
export const useOneTimeSchedule = () => {
  const queryClient = useQueryClient();
  const { mutate } = useMutation({
    mutationFn: (scheduleId: string) => oneTimeSchedule(scheduleId),
    onSuccess: () => {
      toast.success('Schedule started successfully');
      queryClient.invalidateQueries({ queryKey: ['scheduleList'] });
    },
    onError: error => {
      toast.error(error.message);
    },
  });

  return mutate;
};

// 스케쥴 생성 hook - tasntack/mutation
export const useCreateSchedule = () => {
  const queryClient = useQueryClient();
  const { push } = useInternalRouter();

  const { mutate } = useMutation({
    mutationFn: (schedule: CreateScheduleRequest) => createSchedule(schedule),
    onSuccess: () => {
      toast.success('Schedule created successfully');
      queryClient.invalidateQueries({ queryKey: ['scheduleList'] });
      push('/scheduler-management');
    },
    onError: error => {
      toast.error(error.message);
    },
  });

  return mutate;
};

// 스케쥴 삭제 hook - tasntack/mutation
export const useDeleteSchedule = () => {
  const queryClient = useQueryClient();
  const { mutate } = useMutation({
    mutationFn: (scheduleId: string) => deleteSchedule(scheduleId),
    onSuccess: () => {
      toast.success('Schedule deleted successfully');
      queryClient.invalidateQueries({ queryKey: ['scheduleList'] });
    },
    onError: error => {
      toast.error(error.message);
    },
  });

  return mutate;
};

// 스케쥴 수정 hook - tasntack/mutation
export const useUpdateSchedule = () => {
  const queryClient = useQueryClient();
  const { push } = useInternalRouter();
  const { mutate } = useMutation({
    mutationFn: (editScheduleRequest: EditScheduleRequest) => updateSchedule(editScheduleRequest),
    onSuccess: () => {
      toast.success('Schedule updated successfully');
      queryClient.invalidateQueries({ queryKey: ['scheduleList'] });
      push('/scheduler-management');
    },
    onError: error => {
      toast.error(error.message);
    },
  });

  return mutate;
};
