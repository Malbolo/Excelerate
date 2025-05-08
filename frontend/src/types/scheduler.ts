export type Status = 'pending' | 'success' | 'error';

export type FrequencyType = 'daily' | 'weekly' | 'monthly' | string;

export interface FrequencyDisplay {
  type: FrequencyType;
  time: string;
  dayOfWeek?: string;
  dayOfMonth?: number;
}

export interface Command {
  commandId: string;
  commandTitle: string;
  commandStatus: Status;
}

export interface Job {
  id: string;
  order: number;
  title: string;
  description: string;
}

export interface Schedule {
  schedule_id: string;
  title: string;
  description: string;
  frequency: FrequencyType;
  frequency_cron: string;
  frequency_display: FrequencyDisplay;
  is_paused: boolean;
  created_at: string;
  updated_at: string | null;
  start_date: string;
  end_date: string;
  execution_time: string;
  success_emails: string[];
  failure_emails: string[];
  jobs: Job[];
}

export interface DaySchedule {
  pending: Schedule[];
  success: Schedule[];
  error: Schedule[];
}
