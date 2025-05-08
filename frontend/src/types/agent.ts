import { JOB_TYPE } from '@/constant/job';
import { DEPARTMENT } from '@/constant/user';

export interface TLog {
  name: string;
  input: TLogMessage[];
  output: TLogMessage[];
  timestamp: string;
  metadata: TLogMetadata;
  subEvents: TLog[];
}

export interface TLogMetadata {
  [key: string]: TLogMetadata | string | number | null;
}

export interface TLogMessage {
  role: string;
  message: string;
}

export type TJobType = (typeof JOB_TYPE)[keyof typeof JOB_TYPE];

export type TDepartment = (typeof DEPARTMENT)[keyof typeof DEPARTMENT];
