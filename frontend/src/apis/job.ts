import { useMutation, useQueryClient } from '@tanstack/react-query';
import { toast } from 'sonner';

import useInternalRouter from '@/hooks/useInternalRouter';
import { DataFrame } from '@/types/dataframe';

import { api } from './core';

export interface SaveJobRequest {
  type: string;
  title: string;
  description: string;
  data_load_command: string;
  data_load_url: string;
  commands: string[];
  code: string;
}

interface SaveJobResponse {
  job_id: string;
  created_at: string;
}

interface SendCommandListResponse {
  codes: string[];
  dataframe: DataFrame[];
  error_msg: string;
  download_token: string;
  log_id: string;
}

interface GetSourceDataResponse {
  url: string;
  dataframe: DataFrame;
}

interface SendCommandListRequest {
  command_list: string[];
  url: string;
  stream_id: string;
}

const saveJob = async (request: SaveJobRequest) => {
  const { data, error, success } = await api<SaveJobResponse>('/api/jobs', {
    method: 'POST',
    body: JSON.stringify(request),
  });

  if (!success) {
    throw new Error(error);
  }

  return data;
};

const editJob = async (request: SaveJobRequest, jobId: string) => {
  const { data, error, success } = await api<SaveJobResponse>(
    `/api/jobs/${jobId}`,
    {
      method: 'PUT',
      body: JSON.stringify(request),
    },
  );

  if (!success) {
    throw new Error(error);
  }

  return data;
};

const sendCommandList = async ({
  command_list,
  url,
  stream_id,
}: SendCommandListRequest) => {
  const { data, error, success } = await api<SendCommandListResponse>(
    '/api/agent/code/generate',
    {
      method: 'POST',
      body: JSON.stringify({
        command_list,
        url,
        stream_id,
      }),
    },
  );

  if (!success) {
    throw new Error(error);
  }

  return data;
};

const getSourceData = async (command: string) => {
  const { data, error, success } = await api<GetSourceDataResponse>(
    '/api/agent/data/load',
    { method: 'POST', body: JSON.stringify({ command }) },
  );

  if (!success) {
    throw new Error(error);
  }

  return data;
};

export const useSaveJob = () => {
  const queryClient = useQueryClient();
  const { push } = useInternalRouter();
  const { mutateAsync, isPending } = useMutation({
    mutationFn: (request: SaveJobRequest) => saveJob(request),
    onSuccess: () => {
      toast.success('Job saved successfully');
      queryClient.invalidateQueries({ queryKey: ['jobList'] });
      push('/job-management');
    },
    onError: (error: Error) => {
      toast.error(error.message);
    },
  });

  return { mutateAsync, isPending };
};

export const useEditJob = () => {
  const { mutateAsync, isPending } = useMutation({
    mutationFn: ({
      request,
      jobId,
    }: {
      request: SaveJobRequest;
      jobId: string;
    }) => editJob(request, jobId),
    onSuccess: () => {
      toast.success('Job edited successfully');
    },
    onError: (error: Error) => {
      toast.error(error.message);
    },
  });

  return { mutateAsync, isPending };
};

export const useSendCommandList = () => {
  const { mutateAsync, isPending } = useMutation({
    mutationFn: (request: SendCommandListRequest) => sendCommandList(request),
    onError: (error: Error) => {
      toast.error(error.message);
    },
  });

  return { mutateAsync, isPending };
};

export const useGetSourceData = () => {
  const { mutateAsync, isPending } = useMutation({
    mutationFn: (command: string) => getSourceData(command),
    onError: (error: Error) => {
      toast.error(error.message);
    },
  });

  return { mutateAsync, isPending };
};
