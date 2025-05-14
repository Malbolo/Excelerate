import { useGetMonthSchedules } from '@/apis/schedulerMonitoring';

import { getCalendarMatrix } from '../../../lib/getCalendarMatrix';
import CalendarDay from './CalendarDay';

interface CalendarGridProps {
  year: number;
  month: number;
}

const DAYS_OF_WEEK = ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'];

const CalendarGrid = ({ year, month }: CalendarGridProps) => {
  const { data } = useGetMonthSchedules(year.toString(), month.toString());

  const monthSchedules = data.map(({ date, pending, success, failed }) => ({
    day: Number(date.split('-')[2]),
    pending,
    success,
    fail: failed,
  }));

  const matrix = getCalendarMatrix(Number(year), Number(month), monthSchedules);

  return (
    <div className='mx-auto w-full max-w-4xl'>
      <div className='grid grid-cols-7 border-b bg-gray-50 text-center text-xs font-medium text-gray-500'>
        {DAYS_OF_WEEK.map(day => (
          <div key={day} className='py-2'>
            {day}
          </div>
        ))}
      </div>
      <div className='grid grid-cols-7 grid-rows-6 border border-t-0 border-gray-200'>
        {matrix.map((cell, idx) => (
          <CalendarDay
            key={idx}
            day={cell.day.toString()}
            month={month}
            year={year}
            isCurrentMonth={cell.isCurrentMonth}
            pending={cell.pending}
            success={cell.success}
            fail={cell.fail}
          />
        ))}
      </div>
    </div>
  );
};

export default CalendarGrid;
