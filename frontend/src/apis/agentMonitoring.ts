import { useSuspenseQuery } from '@tanstack/react-query';

import { api } from '@/apis/core';
import { TLog } from '@/types/agent';

interface GetJobListRequest {
  user_name: string;
  start_date: string;
  end_date: string;
  page: string;
  size: string;
}

interface LogResponse {
  log_id: string;
  user_name: string;
  agent_name: string;
  log_detail: string;
  total_latency: number;
  created_at: string;
}

interface GetJobListResponse {
  logs: LogResponse[];
  pages: number;
  size: number;
  total: number;
}

const getJobList = async (request: GetJobListRequest) => {
  const { data, error, success } = await api<GetJobListResponse>(
    `/api/agent/logs?&user_name=${request.user_name}&start_date=${request.start_date}&end_date=${request.end_date}&page=${request.page}&size=${request.size}`,
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
      request.user_name,
      request.start_date,
      request.end_date,
      request.page,
      request.size,
    ],
    queryFn: () => getJobList(request),
  });
};

export const useGetJobLogs = (job_id: string) => {
  return useSuspenseQuery({
    queryKey: ['jobLogs', job_id],
    queryFn: () => getJobLogs(job_id),
  });
};
