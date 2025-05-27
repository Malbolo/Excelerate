import { useSuspenseQuery } from '@tanstack/react-query';

import { api } from '@/apis/core';
import { Log } from '@/types/agent';

interface LLMLogListParams {
  user_name: string;
  start_date: string;
  end_date: string;
  page: string;
  size: string;
}

interface LLMLogResponse {
  log_id: string;
  user_name: string;
  agent_name: string;
  log_detail: string;
  total_latency: number;
  created_at: string;
}

interface LLMLogListResponse {
  logs: LLMLogResponse[];
  pages: number;
}

// LLM 로그 목록 조회
const getLLMLogList = async (logListParams: LLMLogListParams) => {
  const params = new URLSearchParams();
  Object.entries(logListParams).forEach(([key, value]) => {
    params.set(key, value);
  });

  const { data, error, success } = await api<LLMLogListResponse>(`/api/agent/logs?${params.toString()}`);

  if (!success) {
    throw new Error(error);
  }

  return data;
};

// LLM 로그 조회
const getLLMLog = async (log_id: string) => {
  const { data, error, success } = await api<Log[]>(`/api/agent/logs/${log_id}`);

  if (!success) {
    throw new Error(error);
  }

  return data;
};

// LLM 로그 목록 조회 hook - tasntack/query
export const useGetLLMLogList = ({ user_name, start_date, end_date, page, size }: LLMLogListParams) => {
  return useSuspenseQuery({
    queryKey: ['jobList', user_name, start_date, end_date, page, size],
    queryFn: () => getLLMLogList({ user_name, start_date, end_date, page, size }),
  });
};

// LLM 로그 조회 hook - tasntack/query
export const useGetLLMLog = (log_id: string) => {
  return useSuspenseQuery({
    queryKey: ['agentLogs', log_id],
    queryFn: () => getLLMLog(log_id),
  });
};
