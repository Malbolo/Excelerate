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
    <div className='mx-auto flex h-[calc(100vh-160px)] max-w-4xl flex-col overflow-hidden rounded-lg border'>
      <div className='grid grid-cols-7 text-center text-xs font-medium'>
        {DAYS_OF_WEEK.map(day => (
          <div key={day} className='py-2 uppercase'>
            {day}
          </div>
        ))}
      </div>
      <div className='grid min-h-0 flex-1 grid-cols-7 grid-rows-6 border-t'>
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
