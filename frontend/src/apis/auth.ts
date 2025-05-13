import {
  useMutation,
  useQueryClient,
  useSuspenseQuery,
} from '@tanstack/react-query';
import { toast } from 'sonner';

import useInternalRouter from '@/hooks/useInternalRouter';
import { LoginFormValues, SignupFormValues } from '@/pages/auth';

import { api } from './core';

interface LoginResponse {
  token: string;
}

interface UserInfoResponse {
  name: string;
  role: string;
}

const getUserInfo = async () => {
  const { data, success } = await api<UserInfoResponse>(
    '/api/users/me/profile',
  );

  if (!success) {
    return null;
  }

  return data;
};

const login = async (request: LoginFormValues) => {
  const { data, error, success } = await api<LoginResponse>(
    '/api/users/login',
    {
      method: 'POST',
      body: JSON.stringify(request),
    },
  );

  if (!success) {
    throw new Error(error);
  }

  return data;
};

const signup = async (request: SignupFormValues) => {
  const { data, error, success } = await api('/api/users', {
    method: 'POST',
    body: JSON.stringify(request),
  });

  if (!success) {
    throw new Error(error);
  }

  return data;
};

export const useGetUserInfoAPI = () =>
  useSuspenseQuery({
    queryKey: ['userInfo'],
    queryFn: getUserInfo,
  });

export const useLoginAPI = () => {
  const queryClient = useQueryClient();
  const { replace } = useInternalRouter();

  const { mutate } = useMutation({
    mutationFn: (request: LoginFormValues) => login(request),
    onSuccess: data => {
      localStorage.setItem('token', data.token);
      toast.success('로그인이 완료되었습니다.');
      queryClient.invalidateQueries({ queryKey: ['userInfo'] });
      replace('/');
    },
    onError: error => {
      toast.error(error.message);
    },
  });

  return mutate;
};

export const useSignupAPI = () => {
  const { mutate } = useMutation({
    mutationFn: (request: SignupFormValues) => signup(request),
    onSuccess: () => {
      toast.success('회원가입이 완료되었습니다.');
    },
    onError: () => {
      toast.error('Failed to signup');
    },
  });

  return mutate;
};
