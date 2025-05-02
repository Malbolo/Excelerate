const BASE_URL = import.meta.env.VITE_BASE_URL;
const ACCESS_TOKEN =
  'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiaWF0IjoxNTE2MjM5MDIyfQ.SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c';

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

export async function api<T>(
  path: string,
  init?: RequestInit,
): Promise<ApiResponse<T>> {
  const url = `${BASE_URL}${path}`;

  const headers: Record<string, string> = {
    'Content-Type': 'application/json',
    ...{ Authorization: 'Bearer ' + ACCESS_TOKEN },
    ...(init?.headers as Record<string, string>),
  };

  const res = await fetch(url, { ...init, headers });
  const { data } = (await res.json()) as DataResponse<T>;

  console.log(res);

  if (!res.ok) {
    console.log(res);
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
