// command -> job -> schedule

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

export interface Schedule {
  scheduleId: string;
  createdAt: string;
  title: string;
  description: string;
  userId: string;
  status: Status;
  jobList: Job[];
}

export interface DaySchedule {
  pending: Schedule[];
  success: Schedule[];
  error: Schedule[];
}
