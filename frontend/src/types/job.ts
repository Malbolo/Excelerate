import { DataFrameRow } from '@/types/dataframe';

export interface TCommand {
  title: string;
  status: TCommandStatus;
}

export type TCommandStatus = 'pending' | 'processing' | 'success' | 'fail';

export interface TMachine extends DataFrameRow {
  machineId: string;
  parameter: string;
  value: number;
  unit: string;
  collectedAt: string;
}
