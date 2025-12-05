# Test Commands Reference - Zario

## 🚀 Quick Commands

```bash
# Run all tests
npm test

# Run specific test file
npm test Formatter.test
npm test Logger.performance

# Run with coverage
npm test -- --coverage

# Watch mode for development
npm test -- --watch

# Verbose output
npm test -- --verbose

# Run specific test suite
npm test -- --testNamePattern="Template Literal"
npm test -- --testNamePattern="Deferred Timestamp"
```

## 📊 Coverage Commands

```bash
# Generate coverage report
npm test -- --coverage

# Generate HTML coverage report
npm test -- --coverage --coverageReporters=html

# View coverage for specific file
npm test -- --coverage --collectCoverageFrom=src/core/Formatter.ts
```

## 🔍 Debugging Commands

```bash
# Run tests with Node debugger
node --inspect-brk node_modules/.bin/jest --runInBand

# Run single test file in debug mode
npm test -- Formatter.test --runInBand
```

## 📝 File Locations