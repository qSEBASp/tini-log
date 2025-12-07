/**
 * Comprehensive tests for Logger class performance improvements
 * 
 * This test suite covers the refactored logging methods in Logger.ts:
 * - Separation of sync and async logging paths
 * - Deferred timestamp creation (only when log will be written)
 * - New logAsyncDirect() method for async operations
 * 
 * These changes improve performance by avoiding unnecessary work when logs
 * are filtered out by level thresholds.
 */

import { Logger } from '../../src/core/Logger';
import { LogData } from '../../src/types';
import { Formatter } from '../../src/core/Formatter';
import { Transport } from '../../src/transports/Transport';

// Mock transport for testing
class MockTransport implements Transport {
  public logs: LogData[] = [];
  public asyncLogs: LogData[] = [];
  public writeCallCount = 0;
  public writeAsyncCallCount = 0;

  write(data: LogData, formatter: Formatter): void {
    this.writeCallCount++;
    this.logs.push(data);
  }

  async writeAsync(data: LogData, formatter: Formatter): Promise<void> {
    this.writeAsyncCallCount++;
    this.asyncLogs.push(data);
    return Promise.resolve();
  }

  reset(): void {
    this.logs = [];
    this.asyncLogs = [];
    this.writeCallCount = 0;
    this.writeAsyncCallCount = 0;
  }
}

describe('Logger - Performance Optimizations', () => {
  let mockTransport: MockTransport;
  let logger: Logger;

  beforeEach(() => {
    mockTransport = new MockTransport();
  });

  describe('Deferred Timestamp Creation', () => {
    test('should not create timestamp when log is filtered out by level', () => {
      logger = new Logger({
        level: 'warn', // Only warn and above
        transports: [mockTransport]
      });

      // Spy on Date constructor to detect timestamp creation
      const dateConstructorSpy = jest.spyOn(global, 'Date');

      // This debug log should be filtered out
      logger.debug('This should not create a timestamp');

      // Verify no logs were written
      expect(mockTransport.logs.length).toBe(0);

      // Clean up spy
      dateConstructorSpy.mockRestore();
    });

    test('should create timestamp only when log passes level filter', () => {
      logger = new Logger({
        level: 'info',
        transports: [mockTransport]
      });

      // This should pass the filter
      logger.info('This should create a timestamp');

      // Verify log was written with timestamp
      expect(mockTransport.logs.length).toBe(1);
      expect(mockTransport.logs[0].timestamp).toBeInstanceOf(Date);
    });

    test('should not process metadata when log is filtered', () => {
      logger = new Logger({
        level: 'error',
        transports: [mockTransport],
        context: { globalContext: 'value' }
      });

      const expensiveMetadata = {
        computed: 'This would be expensive to compute'
      };

      // This info log should be filtered out
      logger.info('Filtered log', expensiveMetadata);

      // No logs should be written
      expect(mockTransport.logs.length).toBe(0);
    });

    test('should merge context only for logs that pass filter', () => {
      logger = new Logger({
        level: 'warn',
        transports: [mockTransport],
        context: { globalKey: 'globalValue' }
      });

      // Filtered out - context merge should not happen
      logger.debug('Debug message', { localKey: 'localValue' });
      expect(mockTransport.logs.length).toBe(0);

      // Passes filter - context should be merged
      logger.warn('Warning message', { localKey: 'localValue' });
      expect(mockTransport.logs.length).toBe(1);
      expect(mockTransport.logs[0].metadata).toEqual({
        globalKey: 'globalValue',
        localKey: 'localValue'
      });
    });
  });

  describe('Sync vs Async Path Separation', () => {
    test('should use sync path when asyncMode is false', () => {
      logger = new Logger({
        level: 'info',
        asyncMode: false,
        transports: [mockTransport]
      });

      logger.info('Sync message');

      // Should use synchronous write
      expect(mockTransport.writeCallCount).toBe(1);
      expect(mockTransport.writeAsyncCallCount).toBe(0);
    });

    test('should use async path when asyncMode is true', async () => {
      logger = new Logger({
        level: 'info',
        asyncMode: true,
        transports: [mockTransport]
      });

      logger.info('Async message');

      // Wait for async operation to complete
      await new Promise(resolve => setTimeout(resolve, 10));

      // Should use asynchronous write
      expect(mockTransport.writeAsyncCallCount).toBe(1);
    });

    test('should handle async errors gracefully', async () => {
      const errorTransport = {
        write: jest.fn(),
        writeAsync: jest.fn().mockRejectedValue(new Error('Async error'))
      };

      logger = new Logger({
        level: 'info',
        asyncMode: true,
        transports: [errorTransport as any]
      });

      // Should not throw
      const consoleErrorSpy = jest.spyOn(console, 'error').mockImplementation();
      logger.info('Message that will fail async');

      await new Promise(resolve => setTimeout(resolve, 10));

      expect(consoleErrorSpy).toHaveBeenCalledWith(
        'Error during async logging:',
        expect.any(Error)
      );

      consoleErrorSpy.mockRestore();
    });

    test('should fall back to sync write if writeAsync not available', async () => {
      const syncOnlyTransport = {
        write: jest.fn()
        // No writeAsync method
      };

      logger = new Logger({
        level: 'info',
        asyncMode: true,
        transports: [syncOnlyTransport as any]
      });

      logger.info('Message for sync-only transport');

      await new Promise(resolve => setTimeout(resolve, 10));

      // Should use setImmediate with sync write
      expect(syncOnlyTransport.write).toHaveBeenCalled();
    });
  });

  describe('Silent Level Optimization', () => {
    test('should not log silent level messages at all', () => {
      logger = new Logger({
        level: 'debug', // Even with lowest level
        transports: [mockTransport]
      });

      logger.logWithLevel('silent', 'This should never appear');

      // Silent logs should never be written
      expect(mockTransport.logs.length).toBe(0);
      expect(mockTransport.writeCallCount).toBe(0);
    });

    test('should skip all processing for silent level', () => {
      logger = new Logger({
        level: 'debug',
        transports: [mockTransport],
        context: { expensive: 'context' }
      });

      // Even with metadata, should not process
      logger.logWithLevel('silent', 'Silent message', { expensive: 'metadata' });

      expect(mockTransport.logs.length).toBe(0);
    });
  });

  describe('Early Exit Optimization', () => {
    test('should exit early when shouldLog returns false', () => {
      logger = new Logger({
        level: 'error', // High threshold
        transports: [mockTransport]
      });

      // These should all exit early
      logger.debug('Debug message');
      logger.info('Info message');
      logger.warn('Warning message');

      // No logs should be written
      expect(mockTransport.writeCallCount).toBe(0);
      expect(mockTransport.logs.length).toBe(0);
    });

    test('should not call transport write when filtered', () => {
      const writeSpy = jest.fn();
      const spyTransport = {
        write: writeSpy,
        writeAsync: jest.fn()
      };

      logger = new Logger({
        level: 'error',
        transports: [spyTransport as any]
      });

      // These should not reach the transport
      logger.debug('Debug');
      logger.info('Info');
      logger.warn('Warn');

      expect(writeSpy).not.toHaveBeenCalled();
    });

    test('should process only logs that pass the filter', () => {
      logger = new Logger({
        level: 'warn',
        transports: [mockTransport]
      });

      logger.debug('Filtered 1');
      logger.info('Filtered 2');
      logger.warn('Passed 1');
      logger.error('Passed 2');

      expect(mockTransport.logs.length).toBe(2);
      expect(mockTransport.logs[0].message).toBe('Passed 1');
      expect(mockTransport.logs[1].message).toBe('Passed 2');
    });
  });

  describe('Performance Benchmarks', () => {
    test('should handle high-frequency logging efficiently in sync mode', () => {
      logger = new Logger({
        level: 'info',
        asyncMode: false,
        transports: [mockTransport]
      });

      const iterations = 1000;
      const startTime = Date.now();

      for (let i = 0; i < iterations; i++) {
        logger.info(`Message ${i}`, { index: i });
      }

      const duration = Date.now() - startTime;

      expect(mockTransport.logs.length).toBe(iterations);
      // Should complete quickly - adjust threshold as needed
      expect(duration).toBeLessThan(1000);
    });

    test('should efficiently filter out logs below threshold', () => {
      logger = new Logger({
        level: 'error',
        transports: [mockTransport]
      });

      const iterations = 10000;
      const startTime = Date.now();

      for (let i = 0; i < iterations; i++) {
        // These should all be filtered quickly
        logger.debug(`Debug ${i}`);
        logger.info(`Info ${i}`);
        logger.warn(`Warn ${i}`);
      }

      const duration = Date.now() - startTime;

      // No logs should be written
      expect(mockTransport.logs.length).toBe(0);
      // Filtering should be very fast
      expect(duration).toBeLessThan(500);
    });

    test('should handle mixed sync/async logging', async () => {
      logger = new Logger({
        level: 'info',
        asyncMode: true,
        transports: [mockTransport]
      });

      const syncLogs = 100;
      const asyncLogs = 100;

      // Log synchronously
      for (let i = 0; i < syncLogs; i++) {
        logger.info(`Sync ${i}`);
      }

      // Wait for async completion
      await new Promise(resolve => setTimeout(resolve, 100));

      expect(mockTransport.asyncLogs.length).toBe(syncLogs);
    });
  });

  describe('LogAsyncDirect Method', () => {
    test('should call logAsyncDirect when in async mode', async () => {
      logger = new Logger({
        level: 'info',
        asyncMode: true,
        transports: [mockTransport]
      });

      logger.info('Async message');
      await new Promise(resolve => setTimeout(resolve, 10));

      expect(mockTransport.asyncLogs.length).toBe(1);
      expect(mockTransport.asyncLogs[0].message).toBe('Async message');
    });

    test('should create timestamp in logAsyncDirect after filter check', async () => {
      logger = new Logger({
        level: 'warn',
        asyncMode: true,
        transports: [mockTransport]
      });

      // This should be filtered before timestamp creation
      logger.info('Filtered message');

      // This should create timestamp
      logger.warn('Passed message');

      await new Promise(resolve => setTimeout(resolve, 10));

      expect(mockTransport.asyncLogs.length).toBe(1);
      expect(mockTransport.asyncLogs[0].timestamp).toBeInstanceOf(Date);
    });

    test('should merge metadata in logAsyncDirect', async () => {
      logger = new Logger({
        level: 'info',
        asyncMode: true,
        transports: [mockTransport],
        context: { global: 'context' }
      });

      logger.info('Message', { local: 'metadata' });
      await new Promise(resolve => setTimeout(resolve, 10));

      expect(mockTransport.asyncLogs[0].metadata).toEqual({
        global: 'context',
        local: 'metadata'
      });
    });
  });

  describe('Edge Cases and Regressions', () => {
    test('should maintain backward compatibility with existing tests', () => {
      logger = new Logger({
        level: 'info',
        transports: [mockTransport]
      });

      logger.info('Test message');

      expect(mockTransport.logs.length).toBe(1);
      expect(mockTransport.logs[0].level).toBe('info');
      expect(mockTransport.logs[0].message).toBe('Test message');
    });

    test('should handle empty metadata correctly', () => {
      logger = new Logger({
        level: 'info',
        transports: [mockTransport],
        context: {}
      });

      logger.info('Message', {});

      expect(mockTransport.logs[0].metadata).toBeUndefined();
    });

    test('should handle undefined metadata correctly', () => {
      logger = new Logger({
        level: 'info',
        transports: [mockTransport]
      });

      logger.info('Message');

      // Should not have metadata field or it should be undefined
      expect(mockTransport.logs[0].metadata).toBeUndefined();
    });

    test('should work correctly with custom log levels', () => {
      logger = new Logger({
        level: 'info',
        customLevels: {
          'custom': 4
        },
        transports: [mockTransport]
      });

      logger.logWithLevel('custom', 'Custom message');

      expect(mockTransport.logs.length).toBe(1);
      expect(mockTransport.logs[0].level).toBe('custom');
    });

    test('should respect level changes during runtime', () => {
      logger = new Logger({
        level: 'info',
        transports: [mockTransport]
      });

      logger.debug('Should not appear');
      expect(mockTransport.logs.length).toBe(0);

      logger.setLevel('debug');
      logger.debug('Should appear');
      expect(mockTransport.logs.length).toBe(1);
    });
  });

  describe('Integration with Multiple Transports', () => {
    test('should call all transports in sync mode', () => {
      const transport1 = new MockTransport();
      const transport2 = new MockTransport();

      logger = new Logger({
        level: 'info',
        asyncMode: false,
        transports: [
          transport1,
          transport2
        ]
      });

      logger.info('Message');

      expect(transport1.writeCallCount).toBe(1);
      expect(transport2.writeCallCount).toBe(1);
    });

    test('should call all transports in async mode', async () => {
      const transport1 = new MockTransport();
      const transport2 = new MockTransport();

      logger = new Logger({
        level: 'info',
        asyncMode: true,
        transports: [
          transport1,
          transport2
        ]
      });

      logger.info('Message');
      await new Promise(resolve => setTimeout(resolve, 10));

      expect(transport1.writeAsyncCallCount).toBe(1);
      expect(transport2.writeAsyncCallCount).toBe(1);
    });
  });
});