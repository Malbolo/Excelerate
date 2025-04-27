import { useMemo, useState } from 'react';

import {
  addMonths,
  format,
  getDay,
  getDaysInMonth,
  getMonth,
  getYear,
  isSameDay,
  isValid,
  setDate,
  setMonth,
  setYear,
  startOfMonth,
  subMonths,
} from 'date-fns';
import { ko } from 'date-fns/locale';
import { ChevronLeftIcon, ChevronRightIcon } from 'lucide-react';

import { Button } from '@/components/ui/button';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';

interface DayPickerProps {
  currentDate: Date;
  onSelect: (date: Date) => void;
}

const DayPicker = ({ currentDate, onSelect }: DayPickerProps) => {
  const [displayDate, setDisplayDate] = useState<Date>(
    startOfMonth(currentDate),
  );

  const daysInMonth = getDaysInMonth(displayDate);
  const firstDayOfMonth = getDay(displayDate);

  const daysArray = useMemo(() => {
    const days = [];
    for (let i = 0; i < firstDayOfMonth; i++) days.push(null);
    for (let i = 1; i <= daysInMonth; i++) days.push(i);
    return days;
  }, [displayDate, firstDayOfMonth, daysInMonth]);

  const handleDayClick = (day: number) => {
    const selected = setDate(displayDate, day);
    onSelect(selected);
  };

  const handlePickerMonthChange = (direction: 'prev' | 'next') => {
    setDisplayDate(prev =>
      direction === 'prev' ? subMonths(prev, 1) : addMonths(prev, 1),
    );
  };

  const handlePickerYearSelect = (yearValue: string) => {
    const year = parseInt(yearValue, 10);
    setDisplayDate(prev => setYear(prev, year));
  };

  const handlePickerMonthSelect = (monthValue: string) => {
    const monthIndex = parseInt(monthValue, 10);
    setDisplayDate(prev => setMonth(prev, monthIndex));
  };

  const currentDisplayYear = getYear(displayDate);
  const yearOptions = Array.from(
    { length: 21 },
    (_, i) => currentDisplayYear - 10 + i,
  );
  const monthOptions = Array.from({ length: 12 }, (_, i) => ({
    value: i.toString(),
    label: format(new Date(currentDisplayYear, i), 'MMMM', { locale: ko }),
  }));
  const weekdays = ['일', '월', '화', '수', '목', '금', '토'];

  return (
    <div className='w-80 p-4'>
      <div className='mb-4 flex items-center justify-between'>
        <Button
          variant='ghost'
          size='icon'
          onClick={() => handlePickerMonthChange('prev')}
          className='h-7 w-7'
        >
          <ChevronLeftIcon className='h-4 w-4' />
        </Button>
        <div className='flex w-full items-center justify-center gap-2'>
          <Select
            value={currentDisplayYear.toString()}
            onValueChange={handlePickerYearSelect}
          >
            <SelectTrigger className='h-8 w-[100px] text-sm font-semibold'>
              <SelectValue placeholder='년도' />
            </SelectTrigger>
            <SelectContent>
              {yearOptions.map(year => (
                <SelectItem key={year} value={year.toString()}>
                  {year}년
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
          <Select
            value={getMonth(displayDate).toString()}
            onValueChange={handlePickerMonthSelect}
          >
            <SelectTrigger className='h-8 w-[70px] text-sm font-semibold'>
              <SelectValue placeholder='월' />
            </SelectTrigger>
            <SelectContent>
              {monthOptions.map(month => (
                <SelectItem key={month.value} value={month.value}>
                  {month.label}
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
        </div>
        <Button
          variant='ghost'
          size='icon'
          onClick={() => handlePickerMonthChange('next')}
          className='h-7 w-7'
        >
          <ChevronRightIcon className='h-4 w-4' />
        </Button>
      </div>
      {/* 요일 헤더 */}
      <div className='text-muted-foreground mb-2 grid grid-cols-7 gap-1 text-center text-xs'>
        {weekdays.map(day => (
          <div key={day}>{day}</div>
        ))}
      </div>
      {/* 날짜 그리드 */}
      <div className='grid grid-cols-7 gap-1'>
        {daysArray.map((day, index) => (
          <div key={index} className='flex h-8 items-center justify-center'>
            {day !== null ? (
              <Button
                variant={
                  isValid(currentDate) &&
                  isSameDay(setDate(displayDate, day), currentDate)
                    ? 'default'
                    : 'ghost'
                }
                size='icon'
                className='h-8 w-8 rounded-full text-sm'
                onClick={() => handleDayClick(day)}
              >
                {day}
              </Button>
            ) : (
              <span />
            )}
          </div>
        ))}
      </div>
    </div>
  );
};

export default DayPicker;
