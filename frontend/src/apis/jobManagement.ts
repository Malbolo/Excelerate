import {
  useMutation,
  useQueryClient,
  useSuspenseQuery,
} from '@tanstack/react-query';
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

interface DeleteJobRequestParams {
  id: string;
  page: string;
  keyword: string;
}

const getJobDetail = async (jobId: string) => {
  const { data, error, success } = await api<JobResponse>(`/api/jobs/${jobId}`);

  if (!success) {
    throw new Error(error);
  }

  return data;
};

const deleteJob = async ({ id, page, keyword }: DeleteJobRequestParams) => {
  const { error, success } = await api<JobResponse>(
    `/api/jobs/${id}?page=${page}&keyword=${keyword}`,
    {
      method: 'DELETE',
    },
  );

  if (!success) {
    throw new Error(error);
  }

  return { page: Number(page), keyword, mine: true };
};

export const useDeleteJob = () => {
  const queryClient = useQueryClient();
  const { mutate } = useMutation({
    mutationFn: (requestParams: DeleteJobRequestParams) =>
      deleteJob(requestParams),
    onError: error => {
      toast.error(error.message);
    },
    onSuccess: ({ page, keyword, mine }) => {
      console.log('onSuccess', { page, keyword, mine });
      toast.success('작업이 삭제되었습니다.');
      queryClient.invalidateQueries({
        queryKey: ['jobList', page, keyword],
      });
    },
  });

  return mutate;
};

// 기본적으로 모두 6개씩 조회할 예정이고
// 페이지네이션에서 데이터가 없는경우 1페이지 빈문자열로 조회하는게 좋아서 기본값을 1, 6, '' 로 설정
const getJobList = async (
  page = 1,
  title = '',
  mine = false,
  type = '',
  dep = '',
) => {
  const isMine = mine ? 'True' : 'False';
  const { data, error, success } = await api<JobListResponse>(
    `/api/jobs?mine=${isMine}&page=${page}&size=6&title=${title}&type=${type}&dep=${dep}`,
  );

  if (!success) {
    throw new Error(error);
  }

  return data;
};

export const useGetJobList = (page = 1, keyword = '', mine = false) => {
  return useSuspenseQuery({
    queryKey: ['jobList', page, keyword, mine],
    queryFn: () => getJobList(page, keyword, mine),
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
