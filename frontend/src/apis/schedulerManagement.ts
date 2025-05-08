import { useMutation, useSuspenseQuery } from '@tanstack/react-query';
import { toast } from 'sonner';

import { CreateScheduleFormData } from '@/pages/createScheduler/components/CreateScheduleModal';

import { api } from './core';
import { JobResponse } from './jobManagement';

interface CreateScheduleResponse {
  message: string;
}

export interface ScheduleDetailResponse {
  schedule_id: string;
  title: string;
  description: string;
  frequency: string;
  frequency_display: {
    type: string;
    time: string;
  };
  is_paused: boolean;
  created_at: string;
  updated_at: string | null;
  start_date: string;
  end_date: string;
  execution_time: string;
  success_emails: string[];
  failure_emails: string[];
  jobs: JobResponse[];
}

const createSchedule = async (schedule: CreateScheduleFormData) => {
  const { error, success } = await api<CreateScheduleResponse>(
    '/api/schedules',
    {
      method: 'POST',
      body: JSON.stringify({
        title: schedule.scheduleTitle,
        description: schedule.scheduleDescription,
        jobs: schedule.selectedJobs.map((job, index) => ({
          id: String(job.id),
          order: index + 1,
        })),
        success_emails: [schedule.successEmail],
        failure_emails: [schedule.failEmail],
        start_date: schedule.startDate.toISOString().split('.')[0],
        end_date: schedule.endDate?.toISOString().split('.')[0],
        execution_time: `2025-05-06T${schedule.executionTime}:00`,
        frequency: schedule.interval,
      }),
    },
  );

  if (!success) {
    throw new Error(error);
  }

  return;
};

const getScheduleDetail = async (scheduleId: string) => {
  const { error, success, data } = await api<ScheduleDetailResponse>(
    `/api/schedules/${scheduleId}`,
  );

  if (!success) {
    throw new Error(error);
  }

  return data;
};

const updateSchedule = async (schedule: CreateScheduleFormData) => {
  const { error, success } = await api<CreateScheduleResponse>(
    '/api/schedules',
    {
      method: 'PUT',
      body: JSON.stringify({
        title: schedule.scheduleTitle,
        description: schedule.scheduleDescription,
        jobs: schedule.selectedJobs.map((job, index) => ({
          id: String(job.id),
          order: index + 1,
        })),
        success_emails: [schedule.successEmail],
        failure_emails: [schedule.failEmail],
        start_date: schedule.startDate.toISOString().split('.')[0],
        end_date: schedule.endDate?.toISOString().split('.')[0],
        execution_time: `2025-05-06T${schedule.executionTime}:00`,
        frequency: schedule.interval,
      }),
    },
  );

  if (!success) {
    throw new Error(error);
  }

  return;
};

const toggleSchedule = async (scheduleId: string) => {
  const { error, success } = await api(`/api/schedules/${scheduleId}/toggle`, {
    method: 'POST',
  });

  if (!success) {
    throw new Error(error);
  }

  return;
};

const oneTimeSchedule = async (scheduleId: string) => {
  const { error, success } = await api(`/api/schedules/${scheduleId}/start`, {
    method: 'POST',
  });

  if (!success) {
    throw new Error(error);
  }

  return;
};

export const useGetScheduleDetail = (scheduleId: string) => {
  return useSuspenseQuery({
    queryKey: ['scheduleDetail', scheduleId],
    queryFn: () => getScheduleDetail(scheduleId),
  });
};

export const useToggleSchedule = () => {
  const { mutate } = useMutation({
    mutationFn: (scheduleId: string) => toggleSchedule(scheduleId),
  });

  return mutate;
};

export const useOneTimeSchedule = () => {
  const { mutate } = useMutation({
    mutationFn: (scheduleId: string) => oneTimeSchedule(scheduleId),
  });

  return mutate;
};

export const useCreateSchedule = () => {
  const { mutate } = useMutation({
    mutationFn: (schedule: CreateScheduleFormData) => createSchedule(schedule),
    onSuccess: () => {
      toast.success('스케쥴이 생성되었습니다.');
    },
    onError: error => {
      toast.error(error.message);
    },
  });

  return mutate;
};

export const useUpdateSchedule = () => {
  const { mutate } = useMutation({
    mutationFn: (schedule: CreateScheduleFormData) => updateSchedule(schedule),
    onSuccess: () => {
      toast.success('스케쥴이 수정되었습니다.');
    },
    onError: error => {
      toast.error(error.message);
    },
  });

  return mutate;
};
