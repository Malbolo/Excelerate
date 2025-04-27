import { useCallback, useMemo, useState } from 'react';

import {
  addDays,
  addMonths,
  format,
  isValid,
  parse,
  startOfMonth,
  subDays,
  subMonths,
} from 'date-fns';
import { ko } from 'date-fns/locale';
import { CalendarIcon, ChevronLeftIcon, ChevronRightIcon } from 'lucide-react';
import { useNavigate, useParams } from 'react-router-dom';

import { Button } from '@/components/ui/button';
import {
  Popover,
  PopoverContent,
  PopoverTrigger,
} from '@/components/ui/popover';

import DayPicker from './DayPicker';
import { MonthYearSelector } from './MonthYearSelector';

function SchedulerNavigator() {
  const { dayId, monthId } = useParams<{ dayId?: string; monthId?: string }>();
  const navigate = useNavigate();

  const [isDayPickerOpen, setIsDayPickerOpen] = useState(false);
  const [isMonthPickerOpen, setIsMonthPickerOpen] = useState(false);

  const { viewType, currentDate, displayDate, isValidDate } = useMemo(() => {
    const type = dayId ? 'day' : monthId ? 'month' : 'none';
    const value = dayId || monthId;
    let date: Date = new Date();
    let display: string = '';
    let valid = false;

    if (!value) {
      const today = new Date();
      return {
        viewType: 'day' as const,
        currentDate: today,
        displayDate: format(today, 'yyyy.MM.dd', { locale: ko }),
        isValidDate: true,
      };
    }
    if (type === 'day') {
      date = parse(value, 'yyyy-MM-dd', new Date());
      valid = isValid(date);
      display = valid
        ? format(date, 'yyyy.MM.dd', { locale: ko })
        : format(new Date(), 'yyyy.MM.dd', { locale: ko }) + ' (잘못된 값)';
      if (!valid) {
        console.error(`Invalid dayId: ${value}`);
        date = new Date();
      }
    } else if (type === 'month') {
      date = parse(`${value}-01`, 'yyyy-MM-dd', new Date());
      valid = isValid(date);
      display = valid
        ? format(date, 'yyyy년 MMMM', { locale: ko })
        : format(new Date(), 'yyyy년 MMMM', { locale: ko }) + ' (잘못된 값)';
      if (!valid) {
        console.error(`Invalid monthId: ${value}`);
        date = startOfMonth(new Date());
      }
    } else {
      const today = new Date();
      return {
        viewType: 'day' as const,
        currentDate: today,
        displayDate: format(today, 'yyyy.MM.dd', { locale: ko }),
        isValidDate: true,
      };
    }
    return {
      viewType: type,
      currentDate: date,
      displayDate: display,
      isValidDate: valid,
    };
  }, [dayId, monthId]);

  const handlePrevious = useCallback(() => {
    if (!isValidDate) return;
    if (viewType === 'day') {
      navigate(
        `/scheduler-monitoring/day/${format(subDays(currentDate, 1), 'yyyy-MM-dd')}`,
      );
    } else if (viewType === 'month') {
      navigate(
        `/scheduler-monitoring/month/${format(subMonths(currentDate, 1), 'yyyy-MM')}`,
      );
    }
  }, [navigate, viewType, currentDate, isValidDate]);

  const handleNext = useCallback(() => {
    if (!isValidDate) return;
    if (viewType === 'day') {
      navigate(
        `/scheduler-monitoring/day/${format(addDays(currentDate, 1), 'yyyy-MM-dd')}`,
      );
    } else if (viewType === 'month') {
      navigate(
        `/scheduler-monitoring/month/${format(addMonths(currentDate, 1), 'yyyy-MM')}`,
      );
    }
  }, [navigate, viewType, currentDate, isValidDate]);

  const handleSelectDay = useCallback(
    (selectedDate: Date) => {
      if (viewType !== 'day') return;
      setIsDayPickerOpen(false);
      navigate(
        `/scheduler-monitoring/day/${format(selectedDate, 'yyyy-MM-dd')}`,
      );
    },
    [navigate, viewType],
  );

  const handleSelectMonthYear = useCallback(
    (selectedDate: Date) => {
      if (viewType !== 'month') return;
      setIsMonthPickerOpen(false);
      navigate(
        `/scheduler-monitoring/month/${format(selectedDate, 'yyyy-MM')}`,
      );
    },
    [navigate, viewType],
  );

  return (
    <div className='flex w-full items-center justify-center gap-2 md:gap-4'>
      <Button
        variant='outline'
        size='icon'
        onClick={handlePrevious}
        aria-label={viewType === 'day' ? '이전 날짜' : '이전 달'}
        className='h-9 w-9'
        disabled={!isValidDate}
      >
        <ChevronLeftIcon className='h-5 w-5' />
      </Button>

      {viewType === 'day' ? (
        <Popover open={isDayPickerOpen} onOpenChange={setIsDayPickerOpen}>
          <PopoverTrigger asChild disabled={!isValidDate}>
            <Button
              variant='ghost'
              className='min-w-[150px] rounded px-2 py-1 text-lg font-bold hover:bg-gray-100 disabled:opacity-50 md:text-xl'
              aria-label='날짜 선택'
            >
              {displayDate}
              <CalendarIcon className='ml-1 h-4 w-4 opacity-70 md:ml-2 md:h-5 md:w-5' />
            </Button>
          </PopoverTrigger>
          {isValidDate && (
            <PopoverContent className='w-auto p-0' align='center'>
              <DayPicker currentDate={currentDate} onSelect={handleSelectDay} />
            </PopoverContent>
          )}
        </Popover>
      ) : (
        <Popover open={isMonthPickerOpen} onOpenChange={setIsMonthPickerOpen}>
          <PopoverTrigger asChild disabled={!isValidDate}>
            <Button
              variant='ghost'
              className={`min-w-[150px] rounded px-2 py-1 text-lg font-bold hover:bg-gray-100 disabled:opacity-50 md:min-w-[180px] md:text-xl ${!isValidDate ? 'text-red-500' : ''}`}
              aria-label='월 선택'
            >
              {displayDate}{' '}
              <CalendarIcon className='ml-1 h-4 w-4 opacity-70 md:ml-2 md:h-5 md:w-5' />
            </Button>
          </PopoverTrigger>
          {isValidDate && (
            <PopoverContent className='w-auto p-0' align='center'>
              <MonthYearSelector
                currentDate={currentDate}
                onSelect={handleSelectMonthYear}
              />
            </PopoverContent>
          )}
        </Popover>
      )}
      <Button
        variant='outline'
        size='icon'
        onClick={handleNext}
        aria-label={viewType === 'day' ? '다음 날짜' : '다음 달'}
        className='h-9 w-9'
        disabled={!isValidDate}
      >
        <ChevronRightIcon className='h-5 w-5' />
      </Button>
    </div>
  );
}

export default SchedulerNavigator;
