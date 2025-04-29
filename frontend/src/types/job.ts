export interface TCommand {
  title: string;
  status: TStatus;
}

export type TStatus = 'pending' | 'processing' | 'success' | 'fail';

export interface TMachine {
  machineId: string;
  parameter: string;
  value: number;
  unit: string;
  collectedAt: string;
}