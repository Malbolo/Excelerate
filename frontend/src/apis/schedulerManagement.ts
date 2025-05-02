import { useMutation } from '@tanstack/react-query';
import { toast } from 'sonner';

import { CreateScheduleFormData } from '@/pages/createScheduler/components/CreateScheduleModal';

import { api } from './core';

interface CreateScheduleResponse {
  message: string;
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
          id: job.id,
          order: index + 1,
        })),
        success_email: schedule.successEmail,
        failure_email: schedule.failEmail,
        start_date: schedule.startDate,
        end_date: schedule.endDate,
        execution_time: schedule.executionTime,
        frequency: schedule.interval,
      }),
    },
  );

  if (!success) {
    throw new Error(error);
  }

  return;
};

export const useCreateSchedule = () => {
  const { mutate } = useMutation({
    mutationFn: (schedule: CreateScheduleFormData) => createSchedule(schedule),
    onSuccess: () => {
      toast.success('스케쥴이 생성되었습니다.');
    },
    // post에서는 에러 바운더리로 캐치가 안되서 추가
    onError: error => {
      toast.error(error.message);
    },
  });

  return mutate;
};
