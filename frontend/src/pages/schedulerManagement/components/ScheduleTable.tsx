import {
  Table,
  TableBody,
  TableHead,
  TableHeader,
  TableRow,
} from '@/components/ui/table';

import { dummySchedules } from '../data';
import ScheduleRow from './ScheduleRow';

const ScheduleTable = () => {
  if (!dummySchedules || dummySchedules.length === 0) {
    return (
      <div className='mt-10 text-center text-gray-500'>No schedules found.</div>
    );
  }

  return (
    <div className='rounded-md border'>
      <Table>
        <TableHeader>
          <TableRow>
            <TableHead className='w-[50px]'></TableHead>
            <TableHead className='w-[80px]'>Status</TableHead>
            <TableHead>Schedule</TableHead>
            <TableHead>Owner</TableHead>
            <TableHead className='w-[80px]'>Last Run</TableHead>
            <TableHead>Interval</TableHead>
            <TableHead>Last Run Time</TableHead>
            <TableHead className='w-[150px]'>Actions</TableHead>
          </TableRow>
        </TableHeader>
        <TableBody>
          {dummySchedules.map((schedule, index) => (
            <ScheduleRow
              key={`${schedule.scheduleId}-${index}`}
              schedule={schedule}
            />
          ))}
        </TableBody>
      </Table>
    </div>
  );
};

export default ScheduleTable;
