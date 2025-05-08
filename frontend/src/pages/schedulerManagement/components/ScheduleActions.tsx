import { Pause, Play, PlayCircle } from 'lucide-react';

import { Schedule, useOneTimeSchedule } from '@/apis/schedulerManagement';
import { useToggleSchedule } from '@/apis/schedulerManagement';
import { Button } from '@/components/ui/button';
import {
  Tooltip,
  TooltipContent,
  TooltipProvider,
  TooltipTrigger,
} from '@/components/ui/tooltip';

interface ScheduleActionsProps {
  schedule: Schedule;
}

const ScheduleActions = ({ schedule }: ScheduleActionsProps) => {
  const toggleSchedule = useToggleSchedule();
  const oneTimeSchedule = useOneTimeSchedule();

  const handleRun = (e: React.MouseEvent) => {
    // e.stopPropagation();사용한 이유는, 테이블 시 클릭 시 행 전체가 선택되는 것을 방지하기 위함
    e.stopPropagation();
    toggleSchedule(schedule.schedule_id);
  };

  const handlePause = (e: React.MouseEvent) => {
    // e.stopPropagation();사용한 이유는, 테이블 시 클릭 시 행 전체가 선택되는 것을 방지하기 위함
    e.stopPropagation();
    toggleSchedule(schedule.schedule_id);
  };

  const handleTrigger = (e: React.MouseEvent) => {
    e.stopPropagation();
    oneTimeSchedule(schedule.schedule_id);
  };

  return (
    <TooltipProvider delayDuration={300}>
      <div className='flex items-center space-x-1'>
        <Tooltip>
          <TooltipTrigger asChild>
            <Button
              variant='ghost'
              size='icon'
              onClick={schedule.is_paused ? handleRun : handlePause}
              className='h-7 w-7'
              aria-label={
                schedule.is_paused ? 'Resume Schedule' : 'Pause Schedule'
              }
            >
              {schedule.is_paused ? (
                <Pause className='h-4 w-4' />
              ) : (
                <Play className='h-4 w-4' />
              )}
            </Button>
          </TooltipTrigger>
          <TooltipContent>
            <p>{schedule.is_paused ? 'Pause Schedule' : 'Resume Schedule'}</p>
          </TooltipContent>
        </Tooltip>

        <Tooltip>
          <TooltipTrigger asChild>
            <Button
              variant='ghost'
              size='icon'
              onClick={handleTrigger}
              className='h-7 w-7'
              aria-label='Trigger Schedule Once'
              // disabled={schedule.status === 'success'}
            >
              <PlayCircle className='h-4 w-4' />
            </Button>
          </TooltipTrigger>
          <TooltipContent>
            <p>Trigger Schedule Once</p>
          </TooltipContent>
        </Tooltip>
      </div>
    </TooltipProvider>
  );
};

export default ScheduleActions;
