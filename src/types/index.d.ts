import { LogLevel } from "../core/LogLevel";
import { CustomLogLevelConfig } from "../core/CustomLogLevel";
import { Transport } from "../transports/Transport";
import { ConsoleTransport, ConsoleTransportOptions, FileTransport, FileTransportOptions } from "../transports";

export interface LogData {
  level: LogLevel;
  message: string;
  timestamp: Date;
  metadata?: Record<string, any> | undefined;
  prefix?: string;
}

// Legacy transport options (backward compat)
export interface LegacyTransportOptions {
  type: "console" | "file" | "custom";
  options?: {
    path?: string;
    colorize?: boolean;
    maxSize?: number;
    maxFiles?: number;
  };
  instance?: Transport;
}

// Union type supporting legacy configs and direct transport instances
export type TransportConfig = LegacyTransportOptions | Transport;

export interface LoggerConfig {
  level?: LogLevel;
  colorize?: boolean;
  json?: boolean;
  transports?: TransportConfig[];
  timestampFormat?: string;
  prefix?: string;
  timestamp?: boolean;
  async?: boolean;
}
