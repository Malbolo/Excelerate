import { useMutation, useSuspenseQuery } from '@tanstack/react-query';

import { api } from './core';

type LLMTemplate = {
  [key: string]: string[];
};

interface GetLLMTemplateByCategoryRequest {
  agent: string;
  template_name: string;
}

const getLLMTemplate = async () => {
  const { data, error, success } = await api<LLMTemplate>(
    '/api/agent/prompts/',
  );

  if (!success) {
    throw new Error(error);
  }

  return data;
};

const getLLMTemplateByCategory = async (
  agent: string,
  template_name: string,
) => {
  const { data, error, success } = await api<string[]>(
    `/api/agent/prompts/${agent}/${template_name}`,
  );

  if (!success) {
    throw new Error(error);
  }

  return data;
};

export const useGetLLMTemplate = () => {
  return useSuspenseQuery({
    queryKey: ['llm-template'],
    queryFn: getLLMTemplate,
  });
};

export const useGetLLMTemplateByCategory = () => {
  const { mutateAsync } = useMutation({
    mutationFn: ({ agent, template_name }: GetLLMTemplateByCategoryRequest) =>
      getLLMTemplateByCategory(agent, template_name),
  });

  return mutateAsync;
};
