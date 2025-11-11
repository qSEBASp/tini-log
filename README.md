# dd-tinylog

[![npm version](https://badge.fury.io/js/dd-tinylog.svg)](https://badge.fury.io/js/dd-tinylog)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

A minimal, fast, and feature-rich logging library for Node.js.

`dd-tinylog` is designed to be a dead simple lightweight and easy-to-use logger with support for multiple transports, customizable formatting, and dynamic log levels.

## Features

- **Lightweight and Fast**: Minimal overhead for high-performance applications.
- **Multiple Transports**: Log to the console, files, or create your own custom transports.
- **Customizable Formatting**: Choose between simple text or structured JSON logging.
- **Dynamic Log Levels**: Change the log level at runtime.
- **Customizable Prefix**: Add a custom prefix to all your log messages.
- **Optional Timestamps**: Enable or disable timestamps in your logs.
- **File Rotation**: Automatically rotate log files based on size.
- **TypeScript Support**: Written in TypeScript.

## Installation

```bash
npm install dd-tinylog
```

## Usage

```typescript
// ESM
import { Logger } from 'dd-tinylog';
// CommonJS
const { Logger } = require("dd-tinylog");

// Create a logger instance
const logger = new Logger({
  level: 'info',
  colorize: true,
  transports: [
    { type: 'console' },
    { type: 'file', options: { path: './logs/app.log' } },
  ],
  prefix: '[My-App]',
  timestamp: true,
});

// Log messages
logger.info('Server started on port 3000');
logger.warn('Low disk space');
logger.error('Failed to connect to database', { code: 500 });
logger.debug('This is a debug message');
logger.silent('This message will not be logged');
logger.boring('This message will be logged but not colored');
```

## Child Loggers

Child loggers allow you to create new logger instances that inherit settings from a parent logger and can add their own specific context. This is useful for organizing logs by specific components, requests, or user sessions.

```typescript
// Create a child logger for a specific request
const requestLogger = logger.createChild({
  prefix: '[Request-123]',
  context: { requestId: 'req-123', userId: 'user-abc' },
});

requestLogger.info('Processing incoming request');
requestLogger.debug('Request payload', { data: { key: 'value' } });
requestLogger.error('Failed to process request', { error: 'timeout' });

// Another child logger for a different part of the application
const dbLogger = logger.createChild({
  prefix: '[Database]',
  level: 'debug', // Child logger can override parent's level
});

dbLogger.debug('Connecting to database...');
dbLogger.info('Query executed successfully');
```

## License

This project is licensed under the MIT License. See the [LICENSE](/LICENSE) file for details.

## Uses for this Library

`dd-tinylog` is a flexible logging tool for many kinds of Node.js applications:

* **Web Servers & APIs** – Record requests, errors, and performance data.
* **Command-Line Tools (CLI)** – Display progress, warnings, and errors clearly for users.
* **Background Jobs** – Track scheduled or long-running tasks.
* **Microservices** – Collect logs from multiple services for easier debugging.
* **Development & Testing** – Adjust log levels to show more or less detail while building or testing.

---

## Planned Improvements

We’re working on several new features and enhancements for `dd-tinylog`:

* **Asynchronous Transports** – Write logs in the background to prevent blocking the main application, improving performance under heavy logging.
* **Custom Log Levels** – Define your own log levels beyond the built-in ones like `info` or `error`.
* **Performance Optimizations** – Further reduce overhead and improve log throughput.
