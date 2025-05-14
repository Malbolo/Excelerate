export interface Position {
  x: number;
  y: number;
}

export interface Log {
  name: string;
  input: LogMessage[];
  output: LogMessage[];
  timestamp: string;
  metadata: LogMetadata;
  subEvents: Log[];
}

export interface LogMetadata {
  [key: string]: LogMetadata | string | number | null;
}

export interface LogMessage {
  role: string;
  message: string;
}
