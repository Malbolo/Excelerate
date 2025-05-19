import { useState } from 'react';

import { ChevronDown, ChevronRight } from 'lucide-react';

import { useGetJobListForScheduler } from '@/apis/job';
import { Job } from '@/apis/jobManagement';
import { Schedule } from '@/apis/schedulerManagement';
import JobDisplay from '@/components/JobDisplay';
import StatusIcon from '@/components/StatusIcon';
import { Button } from '@/components/ui/button';
import { TableCell, TableRow } from '@/components/ui/table';
import { useLocalDate } from '@/store/useLocalDate';

import { formatDate, formatDateTime, formatInterval } from '../../../lib/dateFormat';
import ScheduleActions from './ScheduleActions';

interface ScheduleRowProps {
  schedule: Schedule;
}

const ScheduleRow = ({ schedule }: ScheduleRowProps) => {
  const [isExpanded, setIsExpanded] = useState(false);
  const { locale, place } = useLocalDate();
  const [jobList, setJobList] = useState<Job[]>([]);
  const { mutateAsync: getJobListForScheduler, isPending } = useGetJobListForScheduler(
    schedule.jobs.map(job => job.id),
  );

  const clearJobList = (e: React.MouseEvent) => {
    e.stopPropagation();
    setIsExpanded(false);
    setJobList([]);
  };

  const openJobList = async (e: React.MouseEvent) => {
    e.stopPropagation();
    setIsExpanded(true);
    const jobList = await getJobListForScheduler();
    setJobList(jobList.jobs);
  };

  return (
    <>
      <TableRow className='w-full cursor-pointer items-center' data-state={isExpanded ? 'open' : 'closed'}>
        <TableCell className='w-[50px] text-center'>
          <Button variant='ghost' size='icon' onClick={isExpanded ? clearJobList : openJobList} className='h-7 w-7'>
            {isExpanded ? <ChevronDown className='h-4 w-4' /> : <ChevronRight className='h-4 w-4' />}
          </Button>
        </TableCell>

        <TableCell className='font-medium'>{schedule.title}</TableCell>

        <TableCell>{schedule.owner}</TableCell>

        <TableCell>{formatInterval(schedule.frequency_display, locale, place)}</TableCell>

        <TableCell>
          <div className='flex items-center gap-2'>
            <span className='text-sm'>
              {schedule.last_run?.status && <StatusIcon status={schedule.last_run.status} />}
            </span>
            <span className='text-sm'>
              {schedule.last_run?.end_time ? formatDateTime(schedule.last_run.end_time, locale, place) : '-'}
            </span>
          </div>
        </TableCell>
        <TableCell>
          {schedule.next_run && schedule.next_run.data_interval_end
            ? formatDateTime(schedule.next_run.data_interval_end, locale, place)
            : '-'}
        </TableCell>

        <TableCell>{formatDate(schedule.end_date, locale, place)}</TableCell>

        <TableCell className='w-[150px]'>
          <ScheduleActions schedule={schedule} />
        </TableCell>
      </TableRow>

      {isExpanded && (
        <TableRow className='hover:bg-transparent'>
          <TableCell colSpan={8}>
            <div className='flex flex-col gap-2'>
              {isPending ? null : jobList.length > 0 ? (
                jobList.map(job => <JobDisplay key={job.id} title={job.title} job={job} />)
              ) : (
                <p className='px-2 py-1 text-sm text-gray-500'>This schedule has no jobs defined.</p>
              )}
            </div>
          </TableCell>
        </TableRow>
      )}
    </>
  );
};

export default ScheduleRow;
