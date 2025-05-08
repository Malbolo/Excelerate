import { Task } from '@/apis/schedulerMonitoring';

export const getJobStatus = (task: Task): 'success' | 'failed' | 'default' => {
  if (task.status === 'failed') {
    return 'failed';
  }
  if (task.status === 'success') {
    return 'success';
  }
  return 'default';
};
