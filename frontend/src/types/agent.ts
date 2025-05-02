import { JOB_TYPE } from '@/constant/job';
import { DEPARTMENT } from '@/constant/user';

export interface TLog {
  name: string;
  input: string;
  output: string;
  timestamp: string;
  metadata: Record<string, string>;
}

export type TJobType = (typeof JOB_TYPE)[keyof typeof JOB_TYPE];

export type TDepartment = (typeof DEPARTMENT)[keyof typeof DEPARTMENT];
