import { useState } from 'react';

import { ChevronDown, ChevronRight } from 'lucide-react';

import { Schedule } from '@/apis/schedulerManagement';
import StatusIcon from '@/components/StatusIcon';
import { Button } from '@/components/ui/button';
import { TableCell, TableRow } from '@/components/ui/table';
import JobDisplay from '@/pages/scheduleDetail/components/JobDisplay';
import { Status } from '@/types/scheduler';

import { formatDate, formatInterval } from '../utils/formatInterval';
import ScheduleActions from './ScheduleActions';

interface ScheduleRowProps {
  schedule: Schedule & { status: Status };
}

// export const getScheduleStatus = (schedule: Schedule): Status => {
//   return schedule.status;
// };

const ScheduleRow = ({ schedule }: ScheduleRowProps) => {
  const [isExpanded, setIsExpanded] = useState(false);
  // const scheduleStatus = getScheduleStatus(schedule);

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

        <TableCell>{schedule.title}</TableCell>

        <TableCell>{formatInterval(schedule.frequency_display)}</TableCell>

        <TableCell className='w-[80px]'>
          {/* 더미데이터 */}
          <StatusIcon status={schedule.status} />
        </TableCell>

        {/* Last run , Next run, End Date */}
        <TableCell>{formatDate(schedule.execution_time)}</TableCell>
        <TableCell>{formatDate(schedule.execution_time)}</TableCell>
        <TableCell>{formatDate(schedule.execution_time)}</TableCell>

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
              {schedule.jobs.length > 0 ? (
                schedule.jobs.map(job => (
                  <JobDisplay
                    key={job.id}
                    task={{
                      task_id: job.id,
                      job_id: job.id,
                      status: 'failed',
                    }}
                  />
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
