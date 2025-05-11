import { Schedule } from '@/apis/schedulerManagement';

export const formatInterval = (
  interval: Schedule['frequency_display'],
): string => {
  if (!interval) return 'Manual';
  switch (interval.type) {
    case 'daily':
      return `Daily @ ${interval.time}`;
    case 'weekly':
      return `Weekly on ${interval.dayOfWeek} @ ${interval.time}`;
    case 'monthly':
      return `Monthly on day ${interval.dayOfMonth} @ ${interval.time}`;
    default:
      return 'Custom';
  }
};

export const formatDate = (date: string) => {
  return new Date(date).toLocaleString('en-US', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
  });
};

export const formatDateTime = (date: string) => {
  return new Date(date).toLocaleString('en-US', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit',
    hour12: false,
  });
};
