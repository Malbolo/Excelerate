import { useState } from 'react';

import { ChevronDown, ChevronRight } from 'lucide-react';

import StatusIcon from '@/components/StatusIcon';
import { Button } from '@/components/ui/button';
import { TableCell, TableRow } from '@/components/ui/table';
import JobDisplay from '@/pages/scheduleDetail/components/JobDisplay';
import { Schedule, Status } from '@/types/scheduler';

import { formatDate, formatInterval } from '../utils/formatInterval';
import ScheduleActions from './ScheduleActions';

interface ScheduleRowProps {
  schedule: Schedule;
}

export const getScheduleStatus = (schedule: Schedule): Status => {
  return schedule.status;
};

const ScheduleRow = ({ schedule }: ScheduleRowProps) => {
  const [isExpanded, setIsExpanded] = useState(false);
  const scheduleStatus = getScheduleStatus(schedule);

  const toggleExpansion = (e: React.MouseEvent) => {
    e.stopPropagation();
    setIsExpanded(!isExpanded);
  };

  return (
    <>
      <TableRow
        className='hover:bg-muted/50 cursor-pointer'
        data-state={isExpanded ? 'open' : 'closed'}
      >
        <TableCell className='w-[50px] text-center'>
          <Button
            variant='ghost'
            size='icon'
            onClick={toggleExpansion}
            className='h-7 w-7'
          >
            {isExpanded ? (
              <ChevronDown className='h-4 w-4' />
            ) : (
              <ChevronRight className='h-4 w-4' />
            )}
          </Button>
        </TableCell>

        <TableCell className='font-medium'>{schedule.title}</TableCell>

        <TableCell>{schedule.userId}</TableCell>

        <TableCell className='w-[80px]'>
          <StatusIcon status={scheduleStatus} />
        </TableCell>

        <TableCell>{formatInterval(schedule.interval)}</TableCell>

        <TableCell>{formatDate(schedule.lastRunAt)}</TableCell>

        <TableCell className='w-[150px]'>
          <ScheduleActions schedule={schedule} />
        </TableCell>
      </TableRow>

      {isExpanded && (
        <TableRow className='bg-slate-50 hover:bg-slate-50'>
          <TableCell></TableCell>
          <TableCell colSpan={6} className='p-0'>
            <div className='space-y-2 p-4'>
              <h4 className='mb-2 text-sm font-semibold'>
                Jobs for {schedule.title}:
              </h4>
              {schedule.jobList.length > 0 ? (
                schedule.jobList.map(job => (
                  <JobDisplay key={job.jobId} job={job} />
                ))
              ) : (
                <p className='px-2 py-1 text-sm text-gray-500'>
                  This schedule has no jobs defined.
                </p>
              )}
            </div>
          </TableCell>
        </TableRow>
      )}
    </>
  );
};

export default ScheduleRow;
