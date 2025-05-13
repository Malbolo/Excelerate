import { JOB_TYPES_CONFIG } from '@/constant/job';

export type Status = 'pending' | 'success' | 'failed' | 'running';

export interface Command {
  content: string;
  order: number;
}

export type JobType = (typeof JOB_TYPES_CONFIG)[number]['id'];
