import { Schedule } from '@/apis/schedulerManagement';

const convertUtcTimeToLocal = (utcTimeString: string, locale: string, place: string): string => {
  const dummyUtcDateTimeString = `2025-01-01T${utcTimeString}:00Z`;
  const dateObj = new Date(dummyUtcDateTimeString);

  return dateObj.toLocaleTimeString(locale, {
    hour: '2-digit',
    minute: '2-digit',
    hour12: false,
    timeZone: place,
  });
};

export const formatInterval = (interval: Schedule['frequency_display'], locale: string, place: string): string => {
  if (!interval) return 'Manual';

  const localTime = convertUtcTimeToLocal(interval.time, locale, place);

  switch (interval.type) {
    case 'daily':
      return `daily @ ${localTime}`;
    case 'weekly':
      return `weekly @ ${localTime}`;
    case 'monthly':
      return `monthly @ ${localTime}`;
    default:
      return 'custom';
  }
};

export const formatDate = (dateString: string, locale: string, place: string) => {
  const date = new Date(dateString);
  return date.toLocaleDateString(locale, {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    timeZone: place,
  });
};

export const formatDateTime = (dateTimeString: string, locale: string, place: string) => {
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
