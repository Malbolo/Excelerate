export interface TCommand {
  title: string;
  status: TStatus;
}

export type TStatus = 'pending' | 'processing' | 'success' | 'fail';
