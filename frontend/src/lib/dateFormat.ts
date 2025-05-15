import { Schedule } from '@/apis/schedulerManagement';

const convertUtcTimeToLocal = (
  utcTimeString: string,
  locale: string,
  place: string,
): string => {
  const dummyUtcDateTimeString = `2025-01-01T${utcTimeString}:00Z`;
  const dateObj = new Date(dummyUtcDateTimeString);

  return dateObj.toLocaleTimeString(locale, {
    hour: '2-digit',
    minute: '2-digit',
    hour12: false,
    timeZone: place,
  });
};

export const formatInterval = (
  interval: Schedule['frequency_display'],
  locale: string,
  place: string,
): string => {
  if (!interval) return 'Manual';

  const localTime = convertUtcTimeToLocal(interval.time, locale, place);

  switch (interval.type) {
    case 'daily':
      return `매일 @ ${localTime}`;
    case 'weekly':
      return `매주 ${interval.dayOfWeek} @ ${localTime}`;
    case 'monthly':
      return `매월 ${interval.dayOfMonth}일 @ ${localTime}`;
    default:
      return '사용자 지정';
  }
};

export const formatDate = (
  dateString: string,
  locale: string,
  place: string,
) => {
  const date = new Date(dateString);
  return date.toLocaleDateString(locale, {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    timeZone: place,
  });
};

export const formatDateTime = (
  dateTimeString: string,
  locale: string,
  place: string,
) => {
  const date = new Date(dateTimeString);
  return date.toLocaleString(locale, {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit',
    hour12: false,
    timeZone: place,
  });
};
