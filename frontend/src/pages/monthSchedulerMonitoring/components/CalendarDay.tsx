import React from 'react';

import { format } from 'date-fns';
import { enUS } from 'date-fns/locale';
import { ArrowRight } from 'lucide-react';
import { useNavigate } from 'react-router-dom';

import { Button } from '@/components/ui/button';
import { cn } from '@/lib/utils';

import { isBeforeDate, isSameDate } from '../utils/getCalendarMatrix';

interface CalendarDayProps {
  day: number;
  month: number;
  year: number;
  isCurrentMonth: boolean;
}

const CalendarDay: React.FC<CalendarDayProps> = ({
  day,
  month,
  year,
  isCurrentMonth,
}) => {
  const today = new Date();
  const navigate = useNavigate();

  const cellDate = new Date(year, month - 1, day);
  const isToday = isSameDate(cellDate, today);

  const isPast = isBeforeDate(cellDate, today);
  const isFuture = !isToday && !isPast;

  let waitingCount = 0;
  let successCount = 0;
  let failCount = 0;

  if (isCurrentMonth) {
    if (isPast) {
      waitingCount = Math.random() < 0.1 ? Math.floor(Math.random() * 2) : 0;
      successCount = Math.floor(Math.random() * 15);
      failCount = Math.floor(Math.random() * 4);
    } else if (isFuture) {
      waitingCount = Math.floor(Math.random() * 20);
      successCount = 0;
      failCount = 0;
    } else {
      waitingCount = Math.floor(Math.random() * 10);
      successCount = Math.floor(Math.random() * 12);
      failCount = Math.floor(Math.random() * 3);
    }
  }

  const hasData = waitingCount + successCount + failCount > 0;

  const handleDetailClick = (dayId: string) => {
    navigate(`/scheduler-monitoring/day/${dayId}`);
  };

  const formattedDayId = `${year}-${String(month).padStart(2, '0')}-${String(day).padStart(2, '0')}`;

  return (
    <div
      className={cn(
        'relative flex min-h-20 flex-col border p-2',
        isCurrentMonth ? 'bg-white text-gray-900' : 'bg-gray-100 text-gray-400',
        isCurrentMonth &&
          isToday &&
          'border-2 border-blue-500 ring-1 ring-blue-500',
      )}
    >
      <span
        className={cn(
          'mb-1 self-start text-sm',
          isCurrentMonth ? 'text-gray-800' : 'text-gray-400',
          isToday ? 'font-bold text-blue-700' : 'font-medium',
        )}
      >
        {day}
      </span>

      {isCurrentMonth && hasData && (
        <div className='flex w-full flex-grow flex-col items-start justify-center gap-0.5 pl-1 text-xs md:text-sm'>
          {waitingCount > 0 && (
            <div className='flex items-center gap-1.5 text-orange-600'>
              <span>{waitingCount} Pending</span>
            </div>
          )}
          {successCount > 0 && (
            <div className='flex items-center gap-1.5 text-green-600'>
              <span>{successCount} Success</span>
            </div>
          )}
          {failCount > 0 && (
            <div className='flex items-center gap-1.5 text-red-600'>
              <span>{failCount} Failed</span>
            </div>
          )}
        </div>
      )}

      {isCurrentMonth && hasData && (
        <Button
          variant='ghost'
          size='icon'
          className='absolute right-1 bottom-1 h-6 w-6 text-gray-400 hover:text-gray-700'
          onClick={() => handleDetailClick(formattedDayId)}
          aria-label={`View details for ${format(cellDate, 'MMMM d, yyyy', { locale: enUS })}`}
        >
          <ArrowRight className='h-4 w-4' />
        </Button>
      )}
    </div>
  );
};

export default CalendarDay;
