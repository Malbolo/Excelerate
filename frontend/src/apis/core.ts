const COOKIE_NAME = 'your-cookie-name';

export const api = async <T>(path: string, init?: RequestInit): Promise<T> => {
  const url = `https://api.example.com/api/v1${path}`;

  const headers = {
    'Content-Type': 'application/json',
    Authorization: COOKIE_NAME,
    ...(init && init.headers),
  };

  const response = await fetch(url, { ...init, headers });
  const data = await response.json();
  if (!response.ok) throw new Error(data.message);
  return data as T;
};
