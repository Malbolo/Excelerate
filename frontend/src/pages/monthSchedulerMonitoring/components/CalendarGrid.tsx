import { getCalendarMatrix } from '../utils/getCalendarMatrix';
import CalendarDay from './CalendarDay';

interface CalendarGridProps {
  year: number;
  month: number;
}

const DAYS_OF_WEEK = ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'];

const CalendarGrid = ({ year, month }: CalendarGridProps) => {
  const matrix = getCalendarMatrix(year, month);

  return (
    <div className='mx-auto w-[70%]'>
      <div className='grid grid-cols-7 border-b bg-gray-50'>
        {DAYS_OF_WEEK.map(day => (
          <div key={day} className='py-2 text-center font-semibold'>
            {day}
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
            isCurrentMonth={cell.isCurrentMonth}
          />
        ))}
      </div>
    </div>
  );
};

export default CalendarGrid;
