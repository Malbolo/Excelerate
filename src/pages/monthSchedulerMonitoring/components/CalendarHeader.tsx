import React from 'react';

import { ChevronLeft, ChevronRight } from 'lucide-react';

interface CalendarHeaderProps {
  year: number;
  month: number;
  onPrev: () => void;
  onNext: () => void;
}

const CalendarHeader: React.FC<CalendarHeaderProps> = ({
  year,
  month,
  onPrev,
  onNext,
}) => {
  const date = new Date(year, month - 1);
  const monthName = date.toLocaleDateString('ko-KR', { month: 'long' });
  const displayDate = `${year} ${monthName}`;

  return (
    <div className='flex items-center justify-between p-2'>
      <button
        type='button'
        onClick={onPrev}
        aria-label='Previous month'
        className='p-1'
      >
        <ChevronLeft className='h-5 w-5' />
      </button>

      <span className='text-base font-normal'>{displayDate}</span>

      <button
        type='button'
        onClick={onNext}
        aria-label='Next month'
        className='p-1'
      >
        <ChevronRight className='h-5 w-5' />
      </button>
    </div>
  );
};

export default CalendarHeader;
