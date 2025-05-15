import {
  useMutation,
  useQueryClient,
  useSuspenseQuery,
} from '@tanstack/react-query';
import { useNavigate } from 'react-router-dom';
import { toast } from 'sonner';

import { CreateScheduleFormData } from '@/pages/createScheduler/components/ScheduleDialog/scheduleSchema';

import { api } from './core';
import { JobManagement } from './jobManagement';

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
  jobs: JobManagement[];
  last_run: null | {
    end_time: string;
  };
  next_run: null | {
    data_interval_end: string;
  };
}

interface ScheduleListResponse {
  schedules: Schedule[];
}

interface CreateScheduleRequest extends CreateScheduleFormData {
  selectedJobs: JobManagement[];
}

interface EditScheduleRequest {
  schedule: CreateScheduleRequest;
  scheduleId: string;
}

const getScheduleDetail = async (scheduleId: string) => {
  const { error, success, data } = await api<Schedule>(
    `/api/schedules/${scheduleId}`,
  );

  if (!success) {
    throw new Error(error);
  }

  return data;
};

export const useGetScheduleDetail = (scheduleId: string) => {
  return useSuspenseQuery({
    queryKey: ['scheduleDetail', scheduleId],
    queryFn: () => getScheduleDetail(scheduleId),
  });
};

const getScheduleList = async () => {
  const { error, success, data } =
    await api<ScheduleListResponse>('/api/schedules');

  if (!success) {
    throw new Error(error);
  }

  return data;
};

export const useGetScheduleList = () => {
  return useSuspenseQuery({
    queryKey: ['scheduleList'],
    queryFn: getScheduleList,
  });
};

const createSchedule = async (schedule: CreateScheduleRequest) => {
  const { error, success } = await api('/api/schedules', {
    method: 'POST',
    body: JSON.stringify({
      title: schedule.scheduleTitle,
      description: schedule.scheduleDescription,
      jobs: schedule.selectedJobs.map((job, index) => ({
        id: String(job.id),
        order: index + 1,
      })),
      success_emails: schedule.successEmail,
      failure_emails: schedule.failEmail,
      start_date: schedule.startDate,
      end_date: schedule.endDate,
      execution_time: schedule.executionTime,
      frequency: schedule.interval,
    }),
  });

  if (!success) {
    throw new Error(error);
  }

  return;
};

const updateSchedule = async ({
  scheduleId,
  schedule,
}: EditScheduleRequest) => {
  const { error, success } = await api(`/api/schedules/${scheduleId}`, {
    method: 'PATCH',
    body: JSON.stringify({
      title: schedule.scheduleTitle,
      description: schedule.scheduleDescription,
      jobs: schedule.selectedJobs.map((job, index) => ({
        id: String(job.id),
        order: index + 1,
      })),
      success_emails: schedule.successEmail,
      failure_emails: schedule.failEmail,
      start_date: new Date(schedule.startDate.getTime() + 9 * 60 * 60 * 1000)
        .toISOString()
        .split('.')[0],
      end_date: schedule.endDate
        ? new Date(schedule.endDate.getTime() + 9 * 60 * 60 * 1000)
            .toISOString()
            .split('.')[0]
        : undefined,
      execution_time: schedule.executionTime,
      frequency: schedule.interval,
    }),
  });

  if (!success) {
    throw new Error(error);
  }

  return;
};

const toggleSchedule = async (scheduleId: string) => {
  const { error, success } = await api(`/api/schedules/${scheduleId}/toggle`, {
    method: 'PATCH',
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

const deleteSchedule = async (scheduleId: string) => {
  const { error, success } = await api(`/api/schedules/${scheduleId}`, {
    method: 'DELETE',
  });

  if (!success) {
    throw new Error(error);
  }

  return;
};

export const useToggleSchedule = () => {
  const queryClient = useQueryClient();
  const { mutate } = useMutation({
    mutationFn: (scheduleId: string) => toggleSchedule(scheduleId),
    onSuccess: () => {
      toast.success('Schedule toggled successfully');
      queryClient.invalidateQueries({ queryKey: ['scheduleList'] });
      queryClient.invalidateQueries({ queryKey: ['daySchedules'] });
      queryClient.invalidateQueries({ queryKey: ['monthSchedules'] });
      queryClient.invalidateQueries({ queryKey: ['scheduleDetail'] });
    },
    onError: error => {
      toast.error(error.message);
    },
  });

  return mutate;
};

export const useOneTimeSchedule = () => {
  const queryClient = useQueryClient();
  const { mutate } = useMutation({
    mutationFn: (scheduleId: string) => oneTimeSchedule(scheduleId),
    onSuccess: () => {
      toast.success('Schedule started successfully');
      queryClient.invalidateQueries({ queryKey: ['scheduleList'] });
      queryClient.invalidateQueries({ queryKey: ['daySchedules'] });
      queryClient.invalidateQueries({ queryKey: ['monthSchedules'] });
      queryClient.invalidateQueries({ queryKey: ['scheduleDetail'] });
    },
    onError: error => {
      toast.error(error.message);
    },
  });

  return mutate;
};

export const useCreateSchedule = () => {
  const queryClient = useQueryClient();
  const navigate = useNavigate();

  const { mutate } = useMutation({
    mutationFn: (schedule: CreateScheduleRequest) => createSchedule(schedule),
    onSuccess: () => {
      toast.success('Schedule created successfully');
      queryClient.invalidateQueries({ queryKey: ['scheduleList'] });
      queryClient.invalidateQueries({ queryKey: ['daySchedules'] });
      queryClient.invalidateQueries({ queryKey: ['monthSchedules'] });
      queryClient.invalidateQueries({ queryKey: ['scheduleDetail'] });
      navigate('/scheduler-management');
    },
    onError: error => {
      toast.error(error.message);
    },
  });

  return mutate;
};

export const useDeleteSchedule = () => {
  const queryClient = useQueryClient();
  const { mutate } = useMutation({
    mutationFn: (scheduleId: string) => deleteSchedule(scheduleId),
    onSuccess: () => {
      toast.success('Schedule deleted successfully');
      queryClient.invalidateQueries({ queryKey: ['scheduleList'] });
      queryClient.invalidateQueries({ queryKey: ['daySchedules'] });
      queryClient.invalidateQueries({ queryKey: ['monthSchedules'] });
      queryClient.invalidateQueries({ queryKey: ['scheduleDetail'] });
    },
    onError: error => {
      toast.error(error.message);
    },
  });

  return mutate;
};

export const useUpdateSchedule = () => {
  const queryClient = useQueryClient();
  const navigate = useNavigate();
  const { mutate } = useMutation({
    mutationFn: (editScheduleRequest: EditScheduleRequest) =>
      updateSchedule(editScheduleRequest),
    onSuccess: () => {
      toast.success('Schedule updated successfully');
      queryClient.invalidateQueries({ queryKey: ['scheduleList'] });
      queryClient.invalidateQueries({ queryKey: ['daySchedules'] });
      queryClient.invalidateQueries({ queryKey: ['monthSchedules'] });
      queryClient.invalidateQueries({ queryKey: ['scheduleDetail'] });
      navigate('/scheduler-management');
    },
    onError: error => {
      toast.error(error.message);
    },
  });

  return mutate;
};
