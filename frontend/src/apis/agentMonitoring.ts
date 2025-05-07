import { useQuery, useSuspenseQuery } from '@tanstack/react-query';

import { api } from '@/apis/core';
import { TLog } from '@/types/agent';
import { Job } from '@/types/scheduler';

interface GetJobListRequest {
  name: string;
  dep: string;
  type: string;
  page: string;
  size: string;
}

interface GetJobListResponse {
  jobs: Job[];
  page: number;
  size: number;
  total: number;
}

const getJobList = async (request: GetJobListRequest) => {
  const { data, error, success } = await api<GetJobListResponse>(
    `/api/jobs?mine=False&name=${request.name}&dep=${request.dep}&type=${request.type}&page=${request.page}&size=${request.size}`,
  );

  if (!success) {
    throw new Error(error);
  }

  return data;
};

const getJobLogs = async (job_id: string) => {
  const { data, error, success } = await api<TLog[]>(
    `/api/agent/logs/${job_id}`,
  );

  if (!success) {
    throw new Error(error);
  }

  return data;
};

export const useGetJobList = (request: GetJobListRequest) => {
  return useSuspenseQuery({
    queryKey: [
      'jobList',
      request.name,
      request.dep,
      request.type,
      request.page,
      request.size,
    ],
    queryFn: () => getJobList(request),
  });
};

export const useGetJobLogs = (job_id: string) => {
  return useQuery({
    queryKey: ['jobLogs', job_id],
    queryFn: () => getJobLogs(job_id),
  });
};
