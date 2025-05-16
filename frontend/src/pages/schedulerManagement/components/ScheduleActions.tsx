import { useState } from 'react';

import { Pause, Pencil, Play, PlayCircle, Trash } from 'lucide-react';
import { useNavigate } from 'react-router-dom';

import { Schedule, useDeleteSchedule, useOneTimeSchedule } from '@/apis/schedulerManagement';
import { useToggleSchedule } from '@/apis/schedulerManagement';
import {
  AlertDialog,
  AlertDialogAction,
  AlertDialogCancel,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle,
} from '@/components/ui/alert-dialog';
import { Button } from '@/components/ui/button';
import { Tooltip, TooltipContent, TooltipProvider, TooltipTrigger } from '@/components/ui/tooltip';

interface ScheduleActionsProps {
  schedule: Schedule;
}

const ScheduleActions = ({ schedule }: ScheduleActionsProps) => {
  const navigate = useNavigate();
  const [showEditDialog, setShowEditDialog] = useState(false);
  const [showDeleteDialog, setShowDeleteDialog] = useState(false);
  const toggleSchedule = useToggleSchedule();
  const oneTimeSchedule = useOneTimeSchedule();
  const deleteSchedule = useDeleteSchedule();

  const handleRun = (e: React.MouseEvent) => {
    e.stopPropagation();
    toggleSchedule(schedule.schedule_id);
  };

  const handlePause = (e: React.MouseEvent) => {
    e.stopPropagation();
    toggleSchedule(schedule.schedule_id);
  };

  const handleTrigger = (e: React.MouseEvent) => {
    e.stopPropagation();
    oneTimeSchedule(schedule.schedule_id);
  };

  const handleEdit = (e: React.MouseEvent) => {
    e.stopPropagation();
    setShowEditDialog(true);
  };

  const handleConfirmEdit = () => {
    navigate(`/scheduler-management/edit/${schedule.schedule_id}`);
  };

  const handleDelete = (e: React.MouseEvent) => {
    e.stopPropagation();
    setShowDeleteDialog(true);
  };

  const handleConfirmDelete = () => {
    deleteSchedule(schedule.schedule_id);
    setShowDeleteDialog(false);
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
              aria-label={schedule.is_paused ? 'Resume Schedule' : 'Pause Schedule'}
            >
              {schedule.is_paused ? <Play className='h-4 w-4' /> : <Pause className='h-4 w-4' />}
            </Button>
          </TooltipTrigger>
          <TooltipContent>
            <p>{schedule.is_paused ? 'Resume Schedule' : 'Pause Schedule'}</p>
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
            <Button variant='ghost' size='icon' onClick={handleEdit} className='h-7 w-7' aria-label='Edit Schedule'>
              <Pencil className='h-4 w-4' />
            </Button>
          </TooltipTrigger>
          <TooltipContent>
            <p>Edit Schedule</p>
          </TooltipContent>
        </Tooltip>

        <Tooltip>
          <TooltipTrigger asChild>
            <Button variant='ghost' size='icon' onClick={handleDelete} className='h-7 w-7'>
              <Trash className='h-4 w-4' />
            </Button>
          </TooltipTrigger>
          <TooltipContent>
            <p>Delete Schedule</p>
          </TooltipContent>
        </Tooltip>
      </div>

      <AlertDialog open={showEditDialog} onOpenChange={setShowEditDialog}>
        <AlertDialogContent>
          <AlertDialogHeader>
            <AlertDialogTitle>Edit Schedule</AlertDialogTitle>
            <AlertDialogDescription>Would you like to edit this schedule?</AlertDialogDescription>
          </AlertDialogHeader>
          <AlertDialogFooter>
            <AlertDialogCancel>Cancel</AlertDialogCancel>
            <AlertDialogAction onClick={handleConfirmEdit}>Edit</AlertDialogAction>
          </AlertDialogFooter>
        </AlertDialogContent>
      </AlertDialog>

      <AlertDialog open={showDeleteDialog} onOpenChange={setShowDeleteDialog}>
        <AlertDialogContent>
          <AlertDialogHeader>
            <AlertDialogTitle>Delete Schedule</AlertDialogTitle>
            <AlertDialogDescription>Are you sure you want to delete this schedule?</AlertDialogDescription>
          </AlertDialogHeader>
          <AlertDialogFooter>
            <AlertDialogCancel>Cancel</AlertDialogCancel>
            <AlertDialogAction onClick={handleConfirmDelete}>Delete</AlertDialogAction>
          </AlertDialogFooter>
        </AlertDialogContent>
      </AlertDialog>
    </TooltipProvider>
  );
};

export default ScheduleActions;
