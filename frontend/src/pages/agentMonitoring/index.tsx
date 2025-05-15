import { useState } from 'react';

import { format } from 'date-fns';
import { CalendarIcon } from 'lucide-react';
import { useSearchParams } from 'react-router-dom';

import { useGetJobLogs } from '@/apis/agentMonitoring';
import { Button } from '@/components/ui/button';
import { Calendar } from '@/components/ui/calendar';
import { Input } from '@/components/ui/input';
import {
  Popover,
  PopoverContent,
  PopoverTrigger,
} from '@/components/ui/popover';
import useInternalRouter from '@/hooks/useInternalRouter';
import { cn } from '@/lib/utils';

import AgentCallDetail from './components/AgentCallDetail';
import AgentCallList from './components/AgentCallList';

// 유틸 함수로 분리해야함
const disabledDate = (
  date: Date,
  endDate: Date | undefined,
  startDate: Date | undefined,
) => {
  if (endDate && date > endDate) return true;
  if (startDate && date < startDate) return true;
  if (date > new Date(new Date().setHours(0, 0, 0, 0))) return true;
  return false;
};

const AgentMonitoringPage: React.FC = () => {
  const [startDate, setStartDate] = useState<Date>();
  const [endDate, setEndDate] = useState<Date>();
  const [name, setName] = useState<string>('');

  const { push } = useInternalRouter();

  const [searchParams] = useSearchParams();
  const logId = searchParams.get('logId') || '';

  const { data: logs } = useGetJobLogs(logId);

  const handleSearchJobList = () => {
    const searchParams = new URLSearchParams();

    if (name) searchParams.set('name', name);
    if (startDate)
      searchParams.set('startDate', format(startDate, 'yyyy-MM-dd'));
    if (endDate) searchParams.set('endDate', format(endDate, 'yyyy-MM-dd'));

    searchParams.set('page', '1');
    push(`/agent-monitoring?${searchParams.toString()}`);
  };

  return (
    <div className='bg-gradient flex h-screen w-full'>
      <section className='flex h-screen w-[480px] flex-col justify-between gap-5 p-8'>
        <div className='flex w-full flex-col items-center gap-3'>
          <div className='flex w-full items-center gap-3'>
            <Popover>
              <PopoverTrigger asChild>
                <Button
                  variant={'outline'}
                  className={cn(
                    'flex-1 justify-start text-left font-normal',
                    !startDate && 'text-muted-foreground',
                  )}
                >
                  <CalendarIcon className='mr-2 h-4 w-4' />
                  {startDate ? (
                    format(startDate, 'PPP')
                  ) : (
                    <span>Pick a start date</span>
                  )}
                </Button>
              </PopoverTrigger>
              <PopoverContent className='w-auto p-0'>
                <Calendar
                  mode='single'
                  selected={startDate}
                  onSelect={setStartDate}
                  initialFocus
                  disabled={date => disabledDate(date, endDate, startDate)}
                />
              </PopoverContent>
            </Popover>

            <Popover>
              <PopoverTrigger asChild>
                <Button
                  variant={'outline'}
                  className={cn(
                    'flex-1 justify-start text-left font-normal',
                    !endDate && 'text-muted-foreground',
                  )}
                >
                  <CalendarIcon className='mr-2 h-4 w-4' />
                  {endDate ? (
                    format(endDate, 'PPP')
                  ) : (
                    <span>Pick a end date</span>
                  )}
                </Button>
              </PopoverTrigger>
              <PopoverContent className='w-auto p-0'>
                <Calendar
                  mode='single'
                  selected={endDate}
                  onSelect={setEndDate}
                  initialFocus
                  disabled={date => disabledDate(date, endDate, startDate)}
                />
              </PopoverContent>
            </Popover>
          </div>

          <div className='flex w-full items-center gap-3'>
            <div className='relative h-full flex-1'>
              <Input
                value={name}
                onChange={e => setName(e.target.value)}
                onKeyDown={e => e.key === 'Enter' && handleSearchJobList()}
                placeholder='Search employee name'
              />
            </div>
            <Button onClick={handleSearchJobList} className='cursor-pointer'>
              Search
            </Button>
          </div>
        </div>

        <AgentCallList />
      </section>

      <AgentCallDetail logs={logs} />
    </div>
  );
};

export default AgentMonitoringPage;
