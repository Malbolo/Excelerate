import React from 'react';

import { ArrowRight } from 'lucide-react';
import { useNavigate } from 'react-router-dom';

import { Button } from '@/components/ui/button';
import { cn } from '@/lib/utils';

interface CalendarDayProps {
  day: number;
  month: number;
  year: number;
  isCurrentMonth: boolean;
  today: Date;
}

const isSameDate = (date1: Date, date2: Date): boolean => {
  if (!date1 || !date2) return false;
  return (
    date1.getFullYear() === date2.getFullYear() &&
    date1.getMonth() === date2.getMonth() &&
    date1.getDate() === date2.getDate()
  );
};

const isBeforeDate = (date1: Date, date2: Date): boolean => {
  if (!date1 || !date2) return false;
  const d1 = new Date(date1.getFullYear(), date1.getMonth(), date1.getDate());
  const d2 = new Date(date2.getFullYear(), date2.getMonth(), date2.getDate());
  return d1 < d2;
};

const CalendarDay: React.FC<CalendarDayProps> = ({
  day,
  month,
  year,
  isCurrentMonth,
  today,
}) => {
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
    navigate(`/scheduler-monitoring/${dayId}`);
  };

  return (
    <div
      className={cn(
        'relative flex min-h-32 flex-col border p-2',
        isCurrentMonth ? 'bg-white text-gray-900' : 'bg-gray-100 text-gray-400',
        isToday && 'border-2 border-blue-500 ring-1 ring-blue-500',
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
        <div className='flex w-full flex-grow flex-col items-start justify-center gap-0.5 pl-1'>
          {waitingCount > 0 && (
            <div className='flex items-center gap-1.5 text-orange-600'>
              <span>{waitingCount} 건 대기</span>
            </div>
          )}
          {successCount > 0 && (
            <div className='flex items-center gap-1.5 text-green-600'>
              <span>{successCount} 건 성공</span>
            </div>
          )}
          {failCount > 0 && (
            <div className='flex items-center gap-1.5 text-red-600'>
              <span>{failCount} 건 실패</span>
            </div>
          )}
        </div>
      )}

      {isCurrentMonth && hasData && (
        <Button
          variant='ghost'
          size='icon'
          className='absolute right-1 bottom-1 h-6 w-6 text-gray-400 hover:text-gray-700'
          onClick={() => handleDetailClick(`${year}-${month}-${day}`)}
          aria-label={`${year}년 ${month}월 ${day}일 상세 보기`}
        >
          <ArrowRight className='h-4 w-4' />
        </Button>
      )}
    </div>
  );
};

export default CalendarDay;
