import { Job } from '@/types/scheduler';

export const getJobStatus = (job: Job): 'success' | 'error' | 'default' => {
  if (job.commandList.some(cmd => cmd.commandStatus === 'error')) {
    return 'error';
  }
  if (job.commandList.every(cmd => cmd.commandStatus === 'success')) {
    return 'success';
  }
  return 'default';
};
