export type Status = 'pending' | 'success' | 'error';

export interface Command {
  commandId: string;
  commandTitle: string;
  commandStatus: Status;
}

export interface Job {
  title: string;
  description: string;
  createdAt: string;
  jobId: string;
  commandList: Command[];
}

export interface Batch {
  batchId: string;
  createdAt: string;
  title: string;
  description: string;
  userId: string;
  status: Status;
  jobList: Job[];
}

export interface DaySchedule {
  pending: Batch[];
  success: Batch[];
  error: Batch[];
}
