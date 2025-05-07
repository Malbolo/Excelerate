import { useMutation } from '@tanstack/react-query';
import { toast } from 'sonner';

import { TLog } from '@/types/agent';
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
  codes: string[];
  dataframe: DataFrame[];
  error_msg: string;
  logs: TLog[];
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
  url,
}: {
  command_list: string[];
  url: string;
}) => {
  const { data, error, success } = await api<SendCommandListResponse>(
    '/api/agent/code/generate',
    {
      method: 'POST',
      body: JSON.stringify({
        command_list,
        url,
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
      url,
    }: {
      command_list: string[];
      url: string;
    }) => sendCommandList({ command_list, url }),
    onError: (error: Error) => {
      toast.error(error.message);
    },
  });

  return mutateAsync;
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
