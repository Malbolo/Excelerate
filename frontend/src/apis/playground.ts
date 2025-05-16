import { useMutation, useSuspenseQuery } from '@tanstack/react-query';

import { api } from './core';

type LLMTemplate = {
  [key: string]: string[];
};

interface GetLLMTemplateByCategoryRequest {
  agent: string;
  template_name: string;
}

interface GetLLMTemplateByCategoryResponse {
  system: string;
  fewshot: {
    human: string;
    ai: string;
  }[];
  human: string;
}

interface PostCallPromptResponse {
  output: string;
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
  const { data, error, success } = await api<GetLLMTemplateByCategoryResponse>(
    `/api/agent/prompts/${agent}/${template_name}`,
  );

  if (!success) {
    throw new Error(error);
  }

  return data;
};

const postCallPrompt = async (payload: {
  systemPrompt: string;
  fewShots: { human: string; ai: string }[];
  userInput: string;
  variables: Record<string, string>;
}) => {
  const { systemPrompt, fewShots, userInput, variables } = payload;

  const { error, success, data } = await api<PostCallPromptResponse>(
    '/api/agent/prompts/invoke/messages',
    {
      method: 'POST',
      body: JSON.stringify({
        messages: {
          system: systemPrompt,
          fewshot: fewShots.map(fs => ({
            human: fs.human,
            ai: fs.ai,
          })),
          human: userInput,
        },
        variables,
      }),
    },
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

export const usePostCallPrompt = () => {
  const { mutateAsync } = useMutation({
    mutationFn: postCallPrompt,
  });

  return mutateAsync;
};
