import { useMutation } from '@tanstack/react-query';
import { toast } from 'sonner';

import { DataFrame } from '@/types/dataframe';

import { api } from './core';

export interface SaveJobRequest {
  type: string;
  name: string;
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
  code: string;
  dataframe: DataFrame[];
  errorMessage: string;
  logs: Record<string, string>;
}

interface GetSourceDataResponse {
  url: string;
  dataframe: DataFrame;
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

const sendCommandList = async ({
  command_list,
  dataframe,
}: {
  command_list: string[];
  dataframe: string;
}) => {
  const { data, error, success } = await api<SendCommandListResponse>(
    '/code/generate',
    {
      method: 'POST',
      body: JSON.stringify({
        command_list,
        dataframe,
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
    '/data/load',
    { method: 'POST', body: JSON.stringify({ command }) },
  );

  if (!success) {
    throw new Error(error);
  }

  return data;
};

export const useSaveJob = () => {
  const { mutateAsync } = useMutation({
    mutationFn: (request: SaveJobRequest) => saveJob(request),
    onSuccess: () => {
      toast.success('Job saved successfully');
    },
    onError: (error: Error) => {
      toast.error(error.message);
    },
  });

  return mutateAsync;
};

export const useSendCommandList = () => {
  const { mutateAsync } = useMutation({
    mutationFn: ({
      command_list,
      dataframe,
    }: {
      command_list: string[];
      dataframe: string;
    }) => sendCommandList({ command_list, dataframe }),
    onError: (error: Error) => {
      toast.error(error.message);
    },
  });

  return mutateAsync;
};

export const useGetSourceData = () => {
  const { mutateAsync } = useMutation({
    mutationFn: (command: string) => getSourceData(command),
    onError: (error: Error) => {
      toast.error(error.message);
    },
  });

  return mutateAsync;
};
