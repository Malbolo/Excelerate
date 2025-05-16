import { useSuspenseQuery } from '@tanstack/react-query';

import { api } from '@/apis/core';
import { Log } from '@/types/agent';

interface JobListParams {
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

interface JobListResponse {
  logs: LogResponse[];
  pages: number;
}

const getJobList = async (request: JobListParams) => {
  const { data, error, success } = await api<JobListResponse>(
    `/api/agent/logs?&user_name=${request.user_name}&start_date=${request.start_date}&end_date=${request.end_date}&page=${request.page}&size=${request.size}`,
  );

  if (!success) {
    throw new Error(error);
  }

  return data;
};

const getJobLogs = async (log_id: string) => {
  const { data, error, success } = await api<Log[]>(`/api/agent/logs/${log_id}`);

  if (!success) {
    throw new Error(error);
  }

  return data;
};

export const useGetJobList = ({ user_name, start_date, end_date, page, size }: JobListParams) => {
  return useSuspenseQuery({
    queryKey: ['jobList', user_name, start_date, end_date, page, size],
    queryFn: () => getJobList({ user_name, start_date, end_date, page, size }),
  });
};

export const useGetJobLogs = (log_id: string) => {
  return useSuspenseQuery({
    queryKey: ['agentLogs', log_id],
    queryFn: () => getJobLogs(log_id),
  });
};
