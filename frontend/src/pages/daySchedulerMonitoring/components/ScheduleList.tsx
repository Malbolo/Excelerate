import { ChevronRight } from 'lucide-react';
import { useParams } from 'react-router-dom';

import { DaySchedule } from '@/apis/schedulerMonitoring';
import { Button } from '@/components/ui/button';
import useInternalRouter from '@/hooks/useInternalRouter';

interface ScheduleListProps {
  items: DaySchedule[];
}

const ScheduleList = ({ items }: ScheduleListProps) => {
  const { push } = useInternalRouter();
  const { dayId } = useParams<{ dayId: string }>();

  const handleViewDetails = (schedule_id: string, run_id: string) => {
    const url = `/scheduler-monitoring/detail/${dayId}/${schedule_id}/${run_id}`;
    push(url);
  };

  if (!items || items.length === 0) {
    return (
      <div className='flex h-full items-center justify-center'>
        <p className='text-muted-foreground text-sm'>No items available.</p>
      </div>
    );
  }

  return (
    <div className='flow-root'>
      {items.map((item, index) => (
        <div key={`${item.run_id}-${index}`} className='group relative border-b py-3'>
          <div className='flex items-start justify-between gap-4'>
            <div className='min-w-0 flex-1'>
              <h3 className='text-foreground mb-1 truncate text-sm'>{item.title}</h3>
              <p className='text-muted-foreground line-clamp-2 text-xs'>{item.description}</p>
            </div>

            {item.status !== 'pending' && (
              <Button
                variant='ghost'
                size='sm'
                className='shrink-0 rounded-full opacity-0 transition-all group-hover:opacity-100 hover:bg-transparent'
                onClick={() => handleViewDetails(item.schedule_id, item.run_id)}
                aria-label={`View details for ${item.title}`}
              >
                <ChevronRight className='h-4 w-4' />
              </Button>
            )}
          </div>
        </div>
      ))}
    </div>
  );
};

export default ScheduleList;
