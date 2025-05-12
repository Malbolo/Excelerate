import {
  useMutation,
  useQueryClient,
  useSuspenseQuery,
} from '@tanstack/react-query';
import { toast } from 'sonner';

import { api } from './core';

interface GetTemplatesResponse {
  templates: string[];
}

interface CreateTemplateVariables {
  title: string;
  file: File;
}

const getTemplates = async () => {
  const { data, error, success } = await api<GetTemplatesResponse>(
    '/api/agent/template',
  );

  if (!success) {
    throw new Error(error);
  }

  return data;
};

const deleteTemplate = async (templateId: string) => {
  const { data, error, success } = await api(
    `/api/agent/template/${templateId}`,
    {
      method: 'DELETE',
    },
  );

  if (!success) {
    throw new Error(error);
  }

  return data;
};

const createTemplate = async ({ title, file }: CreateTemplateVariables) => {
  const formData = new FormData();
  formData.append('template_name', title);
  formData.append('file', file);

  const { data, error, success } = await api(`/api/agent/template`, {
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

export const useGetTemplates = () =>
  useSuspenseQuery({
    queryKey: ['templates'],
    queryFn: getTemplates,
  });

export const useDeleteTemplate = () => {
  const queryClient = useQueryClient();

  const { mutate } = useMutation({
    mutationFn: deleteTemplate,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['templates'] });
      toast.success('Template deleted successfully');
    },
    onError: error => {
      toast.error(error.message);
    },
  });

  return mutate;
};

export const useCreateTemplate = () => {
  const queryClient = useQueryClient();

  const { mutate } = useMutation({
    mutationFn: createTemplate,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['templates'] });
      toast.success('Template created successfully');
    },
    onError: error => {
      toast.error(error.message);
    },
  });

  return mutate;
};
