import React from 'react';

import { ChevronLeft, ChevronRight } from 'lucide-react';

import { Button } from '@/components/ui/button';

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
    <div className='flex items-center justify-between border-b border-gray-200 px-4 py-3'>
      <Button
        onClick={onPrev}
        className='rounded-full p-1 text-gray-600 transition-colors duration-150 ease-in-out hover:bg-gray-100 hover:text-gray-800 focus:ring-2 focus:ring-gray-300 focus:ring-offset-1 focus:outline-none'
        aria-label='Previous month'
      >
        <ChevronLeft className='h-5 w-5' />
      </Button>

      <span className='text-lg font-semibold text-gray-800'>{displayDate}</span>

      <button
        onClick={onNext}
        className='rounded-full p-1 text-gray-600 transition-colors duration-150 ease-in-out hover:bg-gray-100 hover:text-gray-800 focus:ring-2 focus:ring-gray-300 focus:ring-offset-1 focus:outline-none'
        aria-label='Next month'
      >
        <ChevronRight className='h-5 w-5' />
      </button>
    </div>
  );
};

export default CalendarHeader;
