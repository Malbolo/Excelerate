import React from 'react';

import { format } from 'date-fns';
import { enUS } from 'date-fns/locale';
import { ChevronRight } from 'lucide-react';

import useInternalRouter from '@/hooks/useInternalRouter';
import { cn } from '@/lib/utils';

interface CalendarDayProps {
  day: string;
  month: number;
  year: number;
  isCurrentMonth: boolean;
  pending: number;
  success: number;
  fail: number;
}

const CalendarDay: React.FC<CalendarDayProps> = ({ day, month, year, isCurrentMonth, pending, success, fail }) => {
  const today = new Date();
  const { push } = useInternalRouter();

  const cellDate = new Date(year, month - 1, Number(day));
  const isToday =
    isCurrentMonth &&
    cellDate.getDate() === today.getDate() &&
    cellDate.getMonth() === today.getMonth() &&
    cellDate.getFullYear() === today.getFullYear();

  const hasData = pending + success + fail > 0;

  const handleDetailClick = (dayId: string) => {
    push(`/scheduler-monitoring/day/${dayId}`);
  };

  const formattedDayId = `${year}-${String(month).padStart(2, '0')}-${String(day).padStart(2, '0')}`;

  return (
    <div
      className={cn(
        'group relative flex h-full flex-col border-r border-b p-2 [&:nth-child(7n)]:border-r-0 [&:nth-child(n+36)]:border-b-0',
        isCurrentMonth ? 'bg-white' : 'bg-gray-50 text-gray-400',
        !isCurrentMonth && 'pointer-events-none',
      )}
    >
      <span
        className={cn(
          'self-start text-xs font-medium sm:text-sm',
          isCurrentMonth ? 'text-gray-900' : 'text-gray-400',
          isToday ? 'bg-primary rounded-full px-2 py-0.5 text-white' : '',
        )}
      >
        {day}
      </span>

      {hasData && (
        <div className='mt-1 flex flex-1 flex-col items-start justify-center gap-1 pl-1 text-[0.7rem] leading-tight sm:text-xs'>
          {pending > 0 && (
            <div className='flex items-center gap-1 rounded-full bg-yellow-50 px-2.5 py-1 text-yellow-700 ring-1 ring-yellow-200'>
              <span>{pending}</span>
              <span>Pending</span>
            </div>
          )}
          {success > 0 && (
            <div className='flex items-center gap-1 rounded-full bg-green-50 px-2.5 py-1 text-green-700 ring-1 ring-green-200'>
              <span>{success}</span>
              <span>Success</span>
            </div>
          )}
          {fail > 0 && (
            <div className='flex items-center gap-1 rounded-full bg-red-50 px-2.5 py-1 text-red-700 ring-1 ring-red-200'>
              <span>{fail}</span>
              <span>Failed</span>
            </div>
          )}
        </div>
      )}

      {isCurrentMonth && hasData && (
        <ChevronRight
          onClick={() => handleDetailClick(formattedDayId)}
          aria-label={`View details for ${format(cellDate, 'MMMM d, yyyy', {
            locale: enUS,
          })}`}
          className='group-hover:text-accent-foreground absolute right-2 bottom-2 h-4 w-4 cursor-pointer opacity-0 transition-all group-hover:opacity-100'
        />
      )}
    </div>
  );
};

export default CalendarDay;
