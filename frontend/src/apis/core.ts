import { BASE_URL } from '@/constant/baseURL';

interface DataResponse<T> {
  result: 'success' | 'error';
  data: T;
}

type ApiSuccess<T> = {
  success: true;
  data: T;
  error: null;
};

type ApiFail = {
  success: false;
  data: null;
  error: string;
};

export type ApiResponse<T> = ApiSuccess<T> | ApiFail;

// 모든 API 요청을 커스텀하는 함수
export async function api<T>(path: string, init?: RequestInit): Promise<ApiResponse<T>> {
  const url = `${BASE_URL}${path}`;

  const headers: Record<string, string> = {
    'Content-Type': 'application/json',
    ...(init?.headers as Record<string, string>),
    ...(localStorage.getItem('token') ? { Authorization: 'Bearer ' + localStorage.getItem('token') } : {}),
  };

  if (init?.body instanceof FormData) {
    delete headers['Content-Type'];
  } else {
    if (!headers['Content-Type']) {
      headers['Content-Type'] = 'application/json';
    }
  }

  const res = await fetch(url, { ...init, headers });
  const { data } = (await res.json()) as DataResponse<T>;

  // 요청이 실패했을 때 , 성공했을 때 두가지의 상황에서 모두 tasntack에서 처리할 수 있도록 함
  if (!res.ok) {
    return {
      data: null,
      success: false,
      error: res.statusText,
    };
  }

  return {
    data: data,
    success: true,
    error: null,
  };
}
