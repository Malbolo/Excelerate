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
import { enUS } from 'date-fns/locale';
import { CalendarIcon, ChevronLeftIcon, ChevronRightIcon } from 'lucide-react';
import { useNavigate, useParams } from 'react-router-dom';

import { Button } from '@/components/ui/button';
import {
  Popover,
  PopoverContent,
  PopoverTrigger,
} from '@/components/ui/popover';

import DayPicker from './DayPicker';
import MonthYearSelector from './MonthYearSelector';

const SchedulerNavigator = () => {
  const { dayId, monthId } = useParams<{ dayId: string; monthId: string }>();
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
        displayDate: format(today, 'MM/dd/yyyy', { locale: enUS }),
        isValidDate: true,
      };
    }

    if (type === 'day') {
      date = parse(value, 'yyyy-MM-dd', new Date());
      valid = isValid(date);
      display = valid
        ? format(date, 'MM/dd/yyyy', { locale: enUS })
        : format(new Date(), 'MM/dd/yyyy', { locale: enUS }) +
          ' (Invalid Value)';
      if (!valid) {
        date = new Date();
      }
    } else if (type === 'month') {
      date = parse(`${value}-01`, 'yyyy-MM-dd', new Date());
      valid = isValid(date);
      display = valid
        ? format(date, 'MMMM yyyy', { locale: enUS })
        : format(new Date(), 'MMMM yyyy', { locale: enUS }) +
          ' (Invalid Value)';
      if (!valid) {
        date = startOfMonth(new Date());
      }
    } else {
      const today = new Date();
      return {
        viewType: 'day' as const,
        currentDate: today,
        displayDate: format(today, 'MM/dd/yyyy', { locale: enUS }),
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
    const pathPrefix = '/scheduler-monitoring';
    if (viewType === 'day') {
      const previousDay = subDays(currentDate, 1);
      navigate(`${pathPrefix}/day/${format(previousDay, 'yyyy-MM-dd')}`);
    } else if (viewType === 'month') {
      const previousMonth = subMonths(currentDate, 1);
      navigate(`${pathPrefix}/month/${format(previousMonth, 'yyyy-MM')}`);
    }
  }, [navigate, viewType, currentDate, isValidDate]);

  const handleNext = useCallback(() => {
    if (!isValidDate) return;
    const pathPrefix = '/scheduler-monitoring';
    if (viewType === 'day') {
      const nextDay = addDays(currentDate, 1);
      navigate(`${pathPrefix}/day/${format(nextDay, 'yyyy-MM-dd')}`);
    } else if (viewType === 'month') {
      const nextMonth = addMonths(currentDate, 1);
      navigate(`${pathPrefix}/month/${format(nextMonth, 'yyyy-MM')}`);
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
        aria-label={viewType === 'day' ? 'Previous Day' : 'Previous Month'}
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
              aria-label='Select Date'
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
              aria-label='Select Month'
            >
              {displayDate}
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
        aria-label={viewType === 'day' ? 'Next Day' : 'Next Month'}
        className='h-9 w-9'
        disabled={!isValidDate}
      >
        <ChevronRightIcon className='h-5 w-5' />
      </Button>
    </div>
  );
};

export default SchedulerNavigator;
