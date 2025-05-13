export type Status = 'pending' | 'success' | 'failed' | 'running';

export interface Command {
  content: string;
  order: number;
}
