import { useSuspenseQuery } from '@tanstack/react-query';

import { api } from '@/apis/core';
import { Job } from '@/types/scheduler';

interface GetJobListRequest {
  uid: string;
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
    `/api/jobs?uid=${request.uid}&page=${request.page}&size=${request.size}`,
  );

  if (!success) {
    throw new Error(error);
  }

  return data;
};

export const useGetJobList = (request: GetJobListRequest) => {
  return useSuspenseQuery({
    queryKey: ['jobList', request.uid, request.page, request.size],
    queryFn: () => getJobList(request),
  });
};
