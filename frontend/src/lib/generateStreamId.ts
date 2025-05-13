/**
 * @param length 접두사를 제외한 랜덤 문자열의 길이 (기본값: 8)
 * @returns 'Stream-'로 시작하는 랜덤 문자열
 * @example
 * generateStreamId() // 'Stream-x7f3k9p2'
 * generateStreamId(4) // 'Stream-a1b2'
 */
export const generateStreamId = (length: number = 8): string => {
  const prefix = 'Stream-';
  const characters =
    'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789';
  const randomString = Array.from({ length }, () =>
    characters.charAt(Math.floor(Math.random() * characters.length)),
  ).join('');

  return `${prefix}${randomString}`;
};
