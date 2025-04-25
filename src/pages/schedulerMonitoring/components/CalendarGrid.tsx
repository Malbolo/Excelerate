import React from 'react';

import { getCalendarMatrix } from '../utils/getCalendarMatrix';
import CalendarDay from './CalendarDay';

interface CalendarGridProps {
  year: number;
  month: number;
  today: Date;
}

const daysOfWeek = ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'];

const CalendarGrid: React.FC<CalendarGridProps> = ({ year, month, today }) => {
  const matrix = getCalendarMatrix(year, month);

  return (
    <div className='w-full'>
      <div className='grid grid-cols-7 border-b bg-gray-50'>
        {daysOfWeek.map(d => (
          <div key={d} className='py-2 text-center font-semibold'>
            {d}
          </div>
        ))}
      </div>
      <div className='grid grid-cols-7 grid-rows-6'>
        {matrix.map((cell, idx) => (
          <CalendarDay
            key={idx}
            day={cell.day}
            month={month}
            year={year}
            today={today}
            isCurrentMonth={cell.isCurrentMonth}
          />
        ))}
      </div>
    </div>
  );
};

export default CalendarGrid;
