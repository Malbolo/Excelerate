import React from 'react';

import { format } from 'date-fns';
import { enUS } from 'date-fns/locale';
import { ArrowRight } from 'lucide-react';
import { useNavigate } from 'react-router-dom';

import { Button } from '@/components/ui/button';
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

const CalendarDay: React.FC<CalendarDayProps> = ({
  day,
  month,
  year,
  isCurrentMonth,
  pending,
  success,
  fail,
}) => {
  const today = new Date();
  const navigate = useNavigate();

  const cellDate = new Date(year, month - 1, Number(day));
  const isToday =
    isCurrentMonth &&
    cellDate.getDate() === today.getDate() &&
    cellDate.getMonth() === today.getMonth() &&
    cellDate.getFullYear() === today.getFullYear();

  const hasData = pending + success + fail > 0;

  const handleDetailClick = (dayId: string) => {
    navigate(`/scheduler-monitoring/day/${dayId}`);
  };

  const formattedDayId = `${year}-${String(month).padStart(2, '0')}-${String(day).padStart(2, '0')}`;

  return (
    <div
      className={cn(
        'group relative flex min-h-[6rem] flex-col border-t border-l border-gray-200 p-2 first:border-l-0 sm:min-h-28',
        isCurrentMonth ? 'bg-white' : 'bg-gray-50 text-gray-400',
        isCurrentMonth &&
          isToday &&
          'border-2 border-blue-500 ring-1 ring-blue-500',
        !isCurrentMonth && 'pointer-events-none',
      )}
    >
      <span
        className={cn(
          'self-start text-xs font-medium sm:text-sm',
          isCurrentMonth ? 'text-gray-900' : 'text-gray-400',
          isToday ? 'rounded-full bg-blue-600 px-2 py-0.5 text-white' : '',
        )}
      >
        {day}
      </span>

      {hasData && (
        <div className='mt-1 flex flex-grow flex-col items-start justify-center gap-0.5 pl-1 text-[0.7rem] leading-tight sm:text-xs'>
          {pending > 0 && (
            <div className='flex items-center gap-1 text-yellow-600'>
              <span className='font-medium'>{pending}</span>
              <span>Pending</span>
            </div>
          )}
          {success > 0 && (
            <div className='flex items-center gap-1 text-green-600'>
              <span className='font-medium'>{success}</span>
              <span>Success</span>
            </div>
          )}
          {fail > 0 && (
            <div className='flex items-center gap-1 text-red-600'>
              <span className='font-medium'>{fail}</span>
              <span>Failed</span>
            </div>
          )}
        </div>
      )}

      {isCurrentMonth && hasData && (
        <Button
          variant='outline'
          size='icon'
          className={cn(
            'absolute right-1.5 bottom-1.5 h-7 w-7 rounded-full',
            'opacity-0 transition-all group-hover:scale-110 group-hover:opacity-100',
            'hover:bg-accent hover:text-accent-foreground',
          )}
          onClick={() => handleDetailClick(formattedDayId)}
          aria-label={`View details for ${format(cellDate, 'MMMM d, yyyy', {
            locale: enUS,
          })}`}
        >
          <ArrowRight className='h-4 w-4' />
        </Button>
      )}
    </div>
  );
};

export default CalendarDay;
