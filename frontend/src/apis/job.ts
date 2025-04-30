import { useMutation } from '@tanstack/react-query';
import { toast } from 'sonner';

import { DataFrame } from '@/types/dataframe';

import { api } from './core';

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

const sendCommandList = async (commandList: string[]) => {
  const { data, error, success } = await api<SendCommandListResponse>(
    '/code/generate',
    { method: 'POST', body: JSON.stringify({ command_list: commandList }) },
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

export const useSendCommandList = () => {
  const { mutateAsync } = useMutation({
    mutationFn: (commandList: string[]) => sendCommandList(commandList),
    onError: error => {
      toast.error(error.message);
    },
  });

  return mutateAsync;
};

export const useGetSourceData = () => {
  const { mutateAsync } = useMutation({
    mutationFn: (command: string) => getSourceData(command),
    onError: error => {
      toast.error(error.message);
    },
  });

  return mutateAsync;
};
