import { Pause, Play, PlayCircle, StopCircle } from 'lucide-react';

import { Button } from '@/components/ui/button';
import {
  Tooltip,
  TooltipContent,
  TooltipProvider,
  TooltipTrigger,
} from '@/components/ui/tooltip';
import { Schedule } from '@/types/scheduler';

interface ScheduleActionsProps {
  schedule: Schedule;
}

const ScheduleActions = ({ schedule }: ScheduleActionsProps) => {
  const isActive = schedule.status !== 'pending';

  const handleRun = (e: React.MouseEvent) => {
    // e.stopPropagation();사용한 이유는, 테이블 시 클릭 시 행 전체가 선택되는 것을 방지하기 위함
    e.stopPropagation();
  };

  const handlePause = (e: React.MouseEvent) => {
    // e.stopPropagation();사용한 이유는, 테이블 시 클릭 시 행 전체가 선택되는 것을 방지하기 위함
    e.stopPropagation();
  };

  const handleTrigger = (e: React.MouseEvent) => {
    // e.stopPropagation();사용한 이유는, 테이블 시 클릭 시 행 전체가 선택되는 것을 방지하기 위함
    e.stopPropagation();
  };

  const handleStop = (e: React.MouseEvent) => {
    // e.stopPropagation();사용한 이유는, 테이블 시 클릭 시 행 전체가 선택되는 것을 방지하기 위함
    e.stopPropagation();
  };

  return (
    <TooltipProvider delayDuration={300}>
      <div className='flex items-center space-x-1'>
        <Tooltip>
          <TooltipTrigger asChild>
            <Button
              variant='ghost'
              size='icon'
              onClick={isActive ? handlePause : handleRun}
              className='h-7 w-7'
              aria-label={isActive ? 'Pause Schedule' : 'Resume Schedule'}
            >
              {isActive ? (
                <Pause className='h-4 w-4' />
              ) : (
                <Play className='h-4 w-4' />
              )}
            </Button>
          </TooltipTrigger>
          <TooltipContent>
            <p>{isActive ? 'Pause Schedule' : 'Resume Schedule'}</p>
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
              disabled={schedule.status === 'success'}
            >
              <PlayCircle className='h-4 w-4' />
            </Button>
          </TooltipTrigger>
          <TooltipContent>
            <p>Trigger Schedule Once</p>
          </TooltipContent>
        </Tooltip>
        <Tooltip>
          <TooltipTrigger asChild>
            <Button
              variant='ghost'
              size='icon'
              onClick={handleStop}
              className='h-7 w-7 text-red-600 hover:bg-red-100'
              aria-label='Stop Schedule Execution'
              disabled={!isActive}
            >
              <StopCircle className='h-4 w-4' />
            </Button>
          </TooltipTrigger>
          <TooltipContent>
            <p>Stop Current/Pending Run</p>
          </TooltipContent>
        </Tooltip>
      </div>
    </TooltipProvider>
  );
};

export default ScheduleActions;
