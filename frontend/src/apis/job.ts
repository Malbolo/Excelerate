import { useMutation } from '@tanstack/react-query';
import { toast } from 'sonner';

import { DataFrame } from '@/types/dataframe';

import { api } from './core';

interface SendCommandListResponse {
  code: string;
  dataframe: DataFrame;
  errorMessage: string;
  logs: Record<string, string>;
}

const sendCommandList = async (commandList: string[]) => {
  const { data, error, success } = await api<SendCommandListResponse>(
    '/code_gen/command',
    { method: 'POST', body: JSON.stringify(commandList) },
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
