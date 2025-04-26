import { useState } from 'react';

import { addDays, format, subDays } from 'date-fns';
import { CalendarIcon, ChevronLeftIcon, ChevronRightIcon } from 'lucide-react';
import { useNavigate } from 'react-router-dom';

import { Button } from '@/components/ui/button';
import { Calendar } from '@/components/ui/calendar';
import {
  Popover,
  PopoverContent,
  PopoverTrigger,
} from '@/components/ui/popover';

interface DateNavigatorProps {
  currentDate: Date;
}

export function DateNavigator({ currentDate }: DateNavigatorProps) {
  const [open, setOpen] = useState(false);
  const navigate = useNavigate();

  const handleSelect = (date: Date | undefined) => {
    if (!date) return;
    setOpen(false);
    const formattedDate = format(date, 'yyyy-MM-dd');
    navigate(`/scheduler-monitoring/${formattedDate}`);
  };

  const handlePreviousDay = () => {
    const previousDay = subDays(currentDate, 1);
    const formattedDate = format(previousDay, 'yyyy-MM-dd');
    navigate(`/scheduler-monitoring/${formattedDate}`);
  };

  const handleNextDay = () => {
    const nextDay = addDays(currentDate, 1);
    const formattedDate = format(nextDay, 'yyyy-MM-dd');
    navigate(`/scheduler-monitoring/${formattedDate}`);
  };

  return (
    <div className='flex w-full items-center justify-center gap-4'>
      <Button
        variant='outline'
        size='icon'
        onClick={handlePreviousDay}
        aria-label='Previous Day'
        className='h-9 w-9'
      >
        <ChevronLeftIcon className='h-5 w-5' />
      </Button>

      <Popover open={open} onOpenChange={setOpen}>
        <PopoverTrigger asChild>
          <Button
            variant='ghost'
            className='rounded px-2 py-1 text-2xl font-bold hover:bg-gray-100'
            aria-label='Select Date'
          >
            {format(currentDate, 'yyyy.MM.dd')}
            <CalendarIcon className='ml-2 h-5 w-5 opacity-70' />
          </Button>
        </PopoverTrigger>
        <PopoverContent className='w-auto p-0' align='center'>
          <Calendar
            mode='single'
            selected={currentDate}
            onSelect={handleSelect}
            initialFocus
          />
        </PopoverContent>
      </Popover>

      <Button
        variant='outline'
        size='icon'
        onClick={handleNextDay}
        aria-label='Next Day'
        className='h-9 w-9'
      >
        <ChevronRightIcon className='h-5 w-5' />
      </Button>
    </div>
  );
}
