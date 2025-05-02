import { useMutation, useSuspenseQuery } from '@tanstack/react-query';
import { toast } from 'sonner';

import { api } from './core';

interface CommandResponse {
  content: string;
  order: number;
}

export interface JobResponse {
  id: string;
  type: string;
  title: string;
  description: string;
  data_load_command: string;
  data_load_url: string;
  commands: CommandResponse[];
  code: string;
}

interface JobListResponse {
  jobs: JobResponse[];
  page: number;
  size: number;
  total: number;
}

const getJobDetail = async (jobId: string) => {
  const { data, error, success } = await api<JobResponse>(`/api/jobs/${jobId}`);

  if (!success) {
    throw new Error(error);
  }

  return data;
};

const deleteJob = async (jobId: string) => {
  const { error, success } = await api<JobResponse>(`/api/jobs/${jobId}`, {
    method: 'DELETE',
  });

  if (!success) {
    throw new Error(error);
  }
};

export const useDeleteJob = () => {
  const { mutateAsync } = useMutation({
    mutationFn: (jobId: string) => deleteJob(jobId),
    onError: error => {
      toast.error(error.message);
    },
    onSuccess: () => {
      toast.success('작업이 삭제되었습니다.');
    },
  });

  return { mutateAsync };
};

// 기본적으로 모두 6개씩 조회할 예정이고
// 페이지네이션에서 데이터가 없는경우 1페이지 빈문자열로 조회하는게 좋아서 기본값을 1, 6, '' 로 설정
const getJobList = async (page = 1, size = 6, title = '') => {
  const { data, error, success } = await api<JobListResponse>(
    `/api/jobs?page=${page}&size=${size}&title=${title}`,
  );

  if (!success) {
    throw new Error(error);
  }

  return data;
};

export const useGetJobList = (page = 1, size = 6, title = '') => {
  return useSuspenseQuery({
    queryKey: ['jobList', page, size, title],
    queryFn: () => getJobList(page, size, title),
  });
};

export const useGetJobDetail = () => {
  const { mutateAsync } = useMutation({
    mutationFn: (jobId: string) => getJobDetail(jobId),
    onError: error => {
      toast.error(error.message);
    },
  });

  return mutateAsync;
};
