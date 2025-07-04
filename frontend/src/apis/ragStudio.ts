import { useMutation, useQueryClient, useSuspenseQuery } from '@tanstack/react-query';
import { toast } from 'sonner';

import { api } from './core';

interface GetRagDocumentsResponse {
  doc_id: string;
  file_name: string;
  status: string;
}

interface RagSearchRequest {
  query: string;
  k: number;
}

interface RagSearchResponse {
  query: string;
  answer: string;
  sources: RagSource[];
}

export interface RagSource {
  doc_id: string;
  file_name: string;
  similarity: number;
}

const ragSearch = async (request: RagSearchRequest) => {
  const { data, error, success } = await api<RagSearchResponse>(`/api/agent/rag/search`, {
    method: 'POST',
    body: JSON.stringify(request),
  });

  if (!success) {
    throw new Error(error);
  }

  return data;
};

const getRagDocuments = async () => {
  const { data, error, success } = await api<GetRagDocumentsResponse[]>('/api/agent/rag/list');

  if (!success) {
    throw new Error(error);
  }

  return data;
};

const insertRagDocument = async (file: File) => {
  const formData = new FormData();
  formData.append('file', file);

  const { data, error, success } = await api(`/api/agent/rag/insert`, {
    headers: {
      'Content-Type': 'multipart/form-data',
    },
    method: 'POST',
    body: formData,
  });

  if (!success) {
    throw new Error(error);
  }

  return data;
};

const deleteRagDocument = async (docId: string) => {
  const { error, success } = await api(`/api/agent/rag/documents/${docId}`, {
    method: 'DELETE',
  });

  if (!success) {
    throw new Error(error);
  }

  return;
};

export const useRagSearch = () => {
  const { mutateAsync } = useMutation({
    mutationFn: ragSearch,
    onError: error => {
      toast.error(error.message);
    },
  });

  return mutateAsync;
};

export const useGetRagDocuments = () => {
  return useSuspenseQuery({
    queryKey: ['ragList'],
    queryFn: () => getRagDocuments(),
  });
};

export const useInsertRagDocument = () => {
  const queryClient = useQueryClient();

  const { mutate } = useMutation({
    mutationFn: insertRagDocument,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['ragList'] });
      toast.success('Document inserted successfully');
    },
    onError: error => {
      toast.error(error.message);
    },
  });

  return mutate;
};

export const useDeleteRagDocument = () => {
  const queryClient = useQueryClient();
  const { mutate } = useMutation({
    mutationFn: (docId: string) => deleteRagDocument(docId),
    onSuccess: () => {
      toast.success('Document deleted successfully');
      queryClient.invalidateQueries({ queryKey: ['ragList'] });
    },
    onError: error => {
      toast.error(error.message);
    },
  });

  return mutate;
};
