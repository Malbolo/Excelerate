import { format } from 'date-fns';
import { useNavigate, useParams } from 'react-router-dom';

import { Batch } from '@/types/scheduler';

interface ScheduleListProps {
  items: Batch[];
}

const ScheduleList = ({ items }: ScheduleListProps) => {
  const navigate = useNavigate();
  const { dayId } = useParams<{ dayId: string }>();

  const handleViewDetails = (scheduleId: string) => {
    const url = `/scheduler-monitoring/${dayId}/${scheduleId}`;
    navigate(url);
  };

  if (!items || items.length === 0) {
    return <p className='px-1 py-3 text-sm text-gray-500'>항목이 없습니다.</p>;
  }

  return (
    <div className='flow-root'>
      {items.map((item, index) => (
        <div
          key={`${item.batchId}-${index}`}
          className='group relative border-b border-gray-100 py-3 last:border-b-0'
        >
          <h3 className='mb-1 text-base font-semibold'>{item.title}</h3>
          <p className='text-sm text-gray-600'>{item.description}</p>
          <div className='mt-2'>
            <p className='text-xs text-gray-500'>
              생성일: {format(new Date(item.createdAt), 'yyyy-MM-dd HH:mm')}
            </p>
          </div>

          <button
            className='invisible absolute top-2 right-0 rounded bg-blue-500 px-2 py-1 text-xs text-white opacity-0 shadow-sm transition-opacity group-hover:visible group-hover:opacity-100 hover:bg-blue-600'
            onClick={() => handleViewDetails(item.batchId)}
            aria-label={`${item.title} 상세보기`}
          >
            상세보기
          </button>
        </div>
      ))}
    </div>
  );
};

export default ScheduleList;
