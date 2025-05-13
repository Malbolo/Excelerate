import { JOB_TYPES_CONFIG } from '@/constant/job';

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

export type TJobType = (typeof JOB_TYPES_CONFIG)[number]['id'];
