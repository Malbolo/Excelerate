import { useMutation, useQueryClient, useSuspenseQuery } from '@tanstack/react-query';
import { toast } from 'sonner';

import useInternalRouter from '@/hooks/useInternalRouter';
import { Command } from '@/types/job';

import { api } from './core';

export interface SaveJobRequest {
  type: string;
  title: string;
  description: string;
  data_load_command: string;
  data_load_url: string;
  commands: string[];
  code: string;
  data_load_code?: string;
  source_data: Record<string, string>;
}

export interface JobManagement extends Job {
  type: string;
  user_name: string;
  data_load_command: string;
  data_load_url: string;
  code: string;
  created_at: string;
  source_data: Record<string, string>;
}

export interface Job {
  commands: Command[];
  id: string;
  title: string;
  description: string;
}

interface JobListResponse {
  jobs: JobManagement[];
  total: number;
}

interface GetJobListParams {
  page: number;
  title: string;
  mine: boolean;
  types: string;
  name: string;
}

interface EditJobRequest {
  request: SaveJobRequest;
  jobId: string;
}

// job 목록 조회
const getJobList = async ({ page = 1, title = '', mine = false, types = '', name = '' }: GetJobListParams) => {
  const isMine = mine ? 'True' : 'False';

  const { data, error, success } = await api<JobListResponse>(
    `/api/jobs?mine=${isMine}&page=${page}&size=6&title=${title}&types=${types}&name=${name}`,
  );

  if (!success) {
    throw new Error(error);
  }

  return data;
};

// job 상세 조회
const getJobDetail = async (jobId: string) => {
  const { data, error, success } = await api<JobManagement>(`/api/jobs/${jobId}`);

  if (!success) {
    throw new Error(error);
  }

  return data;
};

// job 저장
const postJob = async (request: SaveJobRequest) => {
  const { data, error, success } = await api('/api/jobs', {
    method: 'POST',
    body: JSON.stringify(request),
  });

  if (!success) {
    throw new Error(error);
  }

  return data;
};

// job 수정
const updateJob = async (request: SaveJobRequest, jobId: string) => {
  const { data, error, success } = await api(`/api/jobs/${jobId}`, {
    method: 'PUT',
    body: JSON.stringify(request),
  });

  if (!success) {
    throw new Error(error);
  }

  return data;
};

// job 삭제
const deleteJob = async (jobId: string) => {
  const { error, success } = await api(`/api/jobs/${jobId}`, {
    method: 'DELETE',
  });

  if (!success) {
    throw new Error(error);
  }
};

// job 목록 조회 hook - tasntack/query
export const useGetJobList = ({ page = 1, mine = false, types = '', title = '', name = '' }) => {
  return useSuspenseQuery({
    queryKey: ['jobList', page, title, mine, types, name],
    queryFn: () => getJobList({ page, title, mine, types, name }),
  });
};

// job 상세 조회 hook - tasntack/query
export const useGetJobDetail = (jobId: string) => {
  return useSuspenseQuery({
    queryKey: ['jobDetail', jobId],
    queryFn: () => getJobDetail(jobId),
  });
};

// job 저장 hook - tasntack/mutation
export const usePostJob = () => {
  const queryClient = useQueryClient();
  const { push } = useInternalRouter();
  const { mutate, isPending } = useMutation({
    mutationFn: (request: SaveJobRequest) => postJob(request),
    onSuccess: () => {
      toast.success('Job saved successfully');
      queryClient.invalidateQueries({ queryKey: ['jobList'] });
      push('/job-management');
    },
    onError: () => {
      toast.error('Failed to save job');
    },
  });

  return { mutate, isPending };
};

// job 수정 hook - tasntack/mutation
export const useUpdateJob = () => {
  const queryClient = useQueryClient();
  const { push } = useInternalRouter();
  const { mutate, isPending } = useMutation({
    mutationFn: ({ request, jobId }: EditJobRequest) => updateJob(request, jobId),
    onSuccess: () => {
      toast.success('Job edited successfully');
      queryClient.invalidateQueries({ queryKey: ['jobList'] });
      push('/job-management');
    },
    onError: () => {
      toast.error('Failed to edit job');
    },
  });

  return { mutate, isPending };
};

// job 삭제 hook - tasntack/mutation
export const useDeleteJob = () => {
  const queryClient = useQueryClient();
  const { push } = useInternalRouter();
  const { mutate } = useMutation({
    mutationFn: (jobId: string) => deleteJob(jobId),
    onError: error => {
      toast.error(error.message);
    },
    onSuccess: () => {
      toast.success('Job deleted successfully');
      queryClient.invalidateQueries({
        queryKey: ['jobList'],
      });
      push('/job-management');
    },
  });

  return mutate;
};
