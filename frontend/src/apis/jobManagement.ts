import {
  useMutation,
  useQueryClient,
  useSuspenseQuery,
} from '@tanstack/react-query';
import { toast } from 'sonner';

import { Command } from '@/types/job';

import { api } from './core';

export interface JobManagement extends Job {
  type: string;
  user_name: string;
  data_load_command: string;
  data_load_url: string;
  code: string;
  created_at: string;
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

const getJobDetail = async (jobId: string) => {
  const { data, error, success } = await api<JobManagement>(
    `/api/jobs/${jobId}`,
  );

  if (!success) {
    throw new Error(error);
  }

  return data;
};

const deleteJob = async (jobId: string) => {
  const { error, success } = await api(`/api/jobs/${jobId}`, {
    method: 'DELETE',
  });

  if (!success) {
    throw new Error(error);
  }
};

export const useDeleteJob = () => {
  const queryClient = useQueryClient();
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
    },
  });

  return mutate;
};

const getJobList = async ({
  page = 1,
  title = '',
  mine = false,
  types = '',
  name = '',
}: GetJobListParams) => {
  const isMine = mine ? 'True' : 'False';

  const { data, error, success } = await api<JobListResponse>(
    `/api/jobs?mine=${isMine}&page=${page}&size=6&title=${title}&types=${types}&name=${name}`,
  );

  if (!success) {
    throw new Error(error);
  }

  return data;
};

export const useGetJobList = ({
  page = 1,
  mine = false,
  types = '',
  title = '',
  name = '',
}) => {
  return useSuspenseQuery({
    queryKey: ['jobList', page, title, mine, types, name],
    queryFn: () => getJobList({ page, title, mine, types, name }),
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
