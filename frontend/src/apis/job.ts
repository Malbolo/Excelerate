import { useMutation } from '@tanstack/react-query';
import { toast } from 'sonner';

import { DataFrame } from '@/types/dataframe';
import { ErrorMessage } from '@/types/job';

import { api } from './core';

interface DataframeResponse {
  codes: string[];
  dataframe: DataFrame;
  download_token: string;
  log_id: string;
  error_msg?: ErrorMessage;
}

interface SourceDataRequest {
  command: string;
  stream_id?: string;
}

interface SourceDataResponse {
  url: string;
  dataframe: DataFrame;
  data_load_code?: string;
  params: {
    [key: string]: string;
  };
}

interface DataframeRequest {
  command_list: string[];
  url: string;
  stream_id: string;
  original_code?: string;
}

// ai agent 기반의 코드 생성
const getDataFrame = async ({ command_list, url, stream_id, original_code }: DataframeRequest) => {
  const { data, error, success } = await api<DataframeResponse>('/api/agent/code/generate', {
    method: 'POST',
    body: JSON.stringify({
      command_list,
      url,
      stream_id,
      original_code,
    }),
  });

  if (!success) {
    throw new Error(error);
  }

  return data;
};

// ai agent 기반으로 원본 데이터 로드
const getSourceData = async ({ command, stream_id }: SourceDataRequest) => {
  const { data, error, success } = await api<SourceDataResponse>('/api/agent/data/load', {
    method: 'POST',
    body: JSON.stringify({ command, stream_id }),
  });

  if (!success) {
    throw new Error(error);
  }

  return data;
};

// ai agent 기반의 코드 생성 hook - tasntack/mutation
export const useGetDataFrame = () => {
  const { mutateAsync, isPending } = useMutation({
    mutationFn: (request: DataframeRequest) => getDataFrame(request),
    onError: () => {
      toast.error('Failed to send command list');
    },
  });

  return { mutateAsync, isPending };
};

// ai agent 기반으로 원본 데이터 로드 hook - tasntack/mutation
export const useGetSourceData = () => {
  const { mutateAsync, isPending } = useMutation({
    mutationFn: (request: SourceDataRequest) => getSourceData(request),
    onError: () => {
      toast.error('Failed to get source data');
    },
  });

  return { mutateAsync, isPending };
};
