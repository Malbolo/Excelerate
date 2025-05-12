import { useSuspenseQuery } from '@tanstack/react-query';

import { api } from '@/apis/core';
import { TLog } from '@/types/agent';

import { JobResponse } from './jobManagement';

interface GetJobListRequest {
  name: string;
  startdate: string;
  enddate: string;
  page: string;
  size: string;
}

interface GetJobListResponse {
  jobs: JobResponse[];
  page: number;
  size: number;
  total: number;
}

const getJobList = async (request: GetJobListRequest) => {
  const { data, error, success } = await api<GetJobListResponse>(
    `/api/jobs?mine=False&name=${request.name}&startdate=${request.startdate}&enddate=${request.enddate}&page=${request.page}&size=${request.size}`,
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
      request.startdate,
      request.enddate,
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
