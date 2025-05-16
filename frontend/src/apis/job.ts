import { useMutation, useQueryClient } from '@tanstack/react-query';
import { toast } from 'sonner';

import useInternalRouter from '@/hooks/useInternalRouter';
import { DataFrame } from '@/types/dataframe';
import { ErrorMessage } from '@/types/job';

import { api } from './core';

export interface SaveJobRequest {
  type: string;
  title: string;
  description: string;
  data_load_command: string;
  data_load_url: string;
  commands: string[];
  code: string;
  data_load_code?: string;
  source_data: Record<string, string>;
}

interface SendCommandListResponse {
  codes: string[];
  dataframe: DataFrame;
  download_token: string;
  log_id: string;
  error_msg?: ErrorMessage;
}

interface GetSourceDataRequest {
  command: string;
  stream_id?: string;
}

interface GetSourceDataResponse {
  url: string;
  dataframe: DataFrame;
  data_load_code?: string;
  params: {
    [key: string]: string;
  };
}

interface SendCommandListRequest {
  command_list: string[];
  url: string;
  stream_id: string;
  original_code?: string;
}

interface EditJobRequest {
  request: SaveJobRequest;
  jobId: string;
}

const saveJob = async (request: SaveJobRequest) => {
  const { data, error, success } = await api('/api/jobs', {
    method: 'POST',
    body: JSON.stringify(request),
  });

  if (!success) {
    throw new Error(error);
  }

  return data;
};

const editJob = async (request: SaveJobRequest, jobId: string) => {
  const { data, error, success } = await api(`/api/jobs/${jobId}`, {
    method: 'PUT',
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
  stream_id,
  original_code,
}: SendCommandListRequest) => {
  const { data, error, success } = await api<SendCommandListResponse>(
    '/api/agent/code/generate',
    {
      method: 'POST',
      body: JSON.stringify({
        command_list,
        url,
        stream_id,
        original_code,
      }),
    },
  );

  if (!success) {
    throw new Error(error);
  }

  return data;
};

const getSourceData = async ({ command, stream_id }: GetSourceDataRequest) => {
  const { data, error, success } = await api<GetSourceDataResponse>(
    '/api/agent/data/load',
    { method: 'POST', body: JSON.stringify({ command, stream_id }) },
  );

  if (!success) {
    throw new Error(error);
  }

  return data;
};

export const useSaveJob = () => {
  const queryClient = useQueryClient();
  const { push } = useInternalRouter();
  const { mutate, isPending } = useMutation({
    mutationFn: (request: SaveJobRequest) => saveJob(request),
    onSuccess: () => {
      toast.success('Job saved successfully');
      queryClient.invalidateQueries({ queryKey: ['jobList'] });
      push('/job-management');
    },
    onError: () => {
      toast.error('Failed to save job');
    },
  });

  return { mutate, isPending };
};

export const useEditJob = () => {
  const queryClient = useQueryClient();
  const { push } = useInternalRouter();
  const { mutate, isPending } = useMutation({
    mutationFn: ({ request, jobId }: EditJobRequest) => editJob(request, jobId),
    onSuccess: () => {
      toast.success('Job edited successfully');
      queryClient.invalidateQueries({ queryKey: ['jobList'] });
      push('/job-management');
    },
    onError: () => {
      toast.error('Failed to edit job');
    },
  });

  return { mutate, isPending };
};

export const useSendCommandList = () => {
  const { mutateAsync, isPending } = useMutation({
    mutationFn: (request: SendCommandListRequest) => sendCommandList(request),
    onError: () => {
      toast.error('Failed to send command list');
    },
  });

  return { mutateAsync, isPending };
};

export const useGetSourceData = () => {
  const { mutateAsync, isPending } = useMutation({
    mutationFn: (request: GetSourceDataRequest) => getSourceData(request),
    onError: () => {
      toast.error('Failed to get source data');
    },
  });

  return { mutateAsync, isPending };
};
