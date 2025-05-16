import { useGetScheduleList } from '@/apis/schedulerManagement';
import { Table, TableBody, TableHead, TableHeader, TableRow } from '@/components/ui/table';

import ScheduleRow from './ScheduleRow';

const ScheduleTable = () => {
  const { data } = useGetScheduleList();

  const { schedules } = data;

  return (
    <div className='rounded-md border'>
      <Table>
        <TableHeader>
          <TableRow>
            <TableHead></TableHead>
            <TableHead>Schedule Title</TableHead>
            <TableHead>Owner</TableHead>
            <TableHead>Interval</TableHead>

            <TableHead>Last Run</TableHead>
            <TableHead>Next Run</TableHead>
            <TableHead>End Date</TableHead>
            <TableHead>Actions</TableHead>
          </TableRow>
        </TableHeader>
        <TableBody>
          {schedules.map((schedule, index) => (
            <ScheduleRow key={`${schedule.schedule_id}-${index}`} schedule={schedule} />
          ))}
        </TableBody>
      </Table>
    </div>
  );
};

export default ScheduleTable;
