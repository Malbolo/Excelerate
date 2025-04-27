import { useState } from 'react';

import { format, getMonth, getYear, setMonth, setYear } from 'date-fns';
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

interface MonthYearSelectorProps {
  currentDate: Date;
  onSelect: (date: Date) => void;
}

export function MonthYearSelector({
  currentDate,
  onSelect,
}: MonthYearSelectorProps) {
  const initialYear = getYear(currentDate);
  const initialMonth = getMonth(currentDate);

  const [displayYear, setDisplayYear] = useState<number>(initialYear);

  const handleMonthSelect = (monthIndex: number) => {
    let newDate = setYear(currentDate, displayYear);
    newDate = setMonth(newDate, monthIndex);
    onSelect(newDate);
  };

  const handlePickerYearChange = (direction: 'prev' | 'next') => {
    setDisplayYear(prev => (direction === 'prev' ? prev - 1 : prev + 1));
  };

  const handlePickerYearSelect = (yearValue: string) => {
    setDisplayYear(parseInt(yearValue, 10));
  };

  const startYear = displayYear - 10;
  const endYear = displayYear + 10;
  const yearOptions = Array.from(
    { length: endYear - startYear + 1 },
    (_, i) => startYear + i,
  );

  return (
    <div className='w-64 p-4'>
      <div className='mb-4 flex items-center justify-between'>
        <Button
          variant='ghost'
          size='icon'
          onClick={() => handlePickerYearChange('prev')}
          className='h-7 w-7'
        >
          <ChevronLeftIcon className='h-4 w-4' />
        </Button>
        <Select
          value={displayYear.toString()}
          onValueChange={handlePickerYearSelect}
        >
          <SelectTrigger className='w-[100px] text-center font-semibold'>
            {' '}
            <SelectValue placeholder='년도 선택' />{' '}
          </SelectTrigger>
          <SelectContent>
            {' '}
            {yearOptions.map(year => (
              <SelectItem key={year} value={year.toString()}>
                {year}년
              </SelectItem>
            ))}{' '}
          </SelectContent>
        </Select>
        <Button
          variant='ghost'
          size='icon'
          onClick={() => handlePickerYearChange('next')}
          className='h-7 w-7'
        >
          <ChevronRightIcon className='h-4 w-4' />
        </Button>
      </div>
      <div className='grid grid-cols-3 gap-2'>
        {Array.from({ length: 12 }).map((_, index) => (
          <Button
            key={index}
            variant={
              initialMonth === index && initialYear === displayYear
                ? 'default'
                : 'ghost'
            }
            size='sm'
            className='text-sm'
            onClick={() => handleMonthSelect(index)}
          >
            {format(new Date(displayYear, index), 'MMM', { locale: ko })}
          </Button>
        ))}
      </div>
    </div>
  );
}

export default MonthYearSelector;
