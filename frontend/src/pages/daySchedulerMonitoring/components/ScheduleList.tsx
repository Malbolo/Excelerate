import { format } from 'date-fns';
import { enUS } from 'date-fns/locale';
import { useNavigate, useParams } from 'react-router-dom';

import { Button } from '@/components/ui/button';
import { Schedule } from '@/types/scheduler';

interface ScheduleListProps {
  items: Schedule[];
}

const ScheduleList = ({ items }: ScheduleListProps) => {
  const navigate = useNavigate();
  const { dayId } = useParams<{ dayId: string }>();

  const handleViewDetails = (scheduleId: string) => {
    const url = `/scheduler-monitoring/detail/${dayId}/${scheduleId}`;
    navigate(url);
  };

  if (!items || items.length === 0) {
    return (
      <p className='px-1 py-3 text-sm text-gray-500'>No items available.</p>
    );
  }

  return (
    <div className='flow-root'>
      {items.map((item, index) => (
        <div
          key={`${item.scheduleId}-${index}`}
          className='group relative border-b border-gray-100 py-3 last:border-b-0'
        >
          <h3 className='mb-1 text-base font-semibold'>{item.title}</h3>
          <p className='text-sm text-gray-600'>{item.description}</p>

          <div className='mt-2'>
            <p className='text-xs text-gray-500'>
              Created:
              {format(new Date(item.createdAt), 'MMM d, yyyy h:mm a', {
                locale: enUS,
              })}
            </p>
          </div>

          <Button
            className='absolute top-2 right-0 rounded bg-blue-500 px-2 py-1 text-xs text-white opacity-0 shadow-sm transition-opacity group-hover:visible group-hover:opacity-100 hover:bg-blue-600'
            onClick={() => handleViewDetails(item.scheduleId)}
            aria-label={`View details for ${item.title}`}
          >
            View Details
          </Button>
        </div>
      ))}
    </div>
  );
};

export default ScheduleList;
