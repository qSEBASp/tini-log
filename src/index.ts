import { Logger } from './core/Logger';
import { LogLevel } from './core/LogLevel';
import { ConsoleTransport, FileTransport, HttpTransport, Transport } from './transports';
import { TransportConfig, LoggerConfig } from './types/index';
import { CustomLogLevelConfig } from './core/CustomLogLevel';

export { Logger, ConsoleTransport, FileTransport, HttpTransport };
export type { LogLevel, Transport, TransportConfig, LoggerConfig, CustomLogLevelConfig };
export default Logger;
