#!/bin/bash

echo "🔍 Zario Test Suite Verification"
echo "================================="
echo ""

# Check if test files exist
echo "📁 Checking test files..."
if [ -f "tests/core/Formatter.test.ts" ]; then
    echo "✅ tests/core/Formatter.test.ts exists ($(wc -l < tests/core/Formatter.test.ts) lines)"
else
    echo "❌ tests/core/Formatter.test.ts NOT FOUND"
fi

if [ -f "tests/core/Logger.performance.test.ts" ]; then
    echo "✅ tests/core/Logger.performance.test.ts exists ($(wc -l < tests/core/Logger.performance.test.ts) lines)"
else
    echo "❌ tests/core/Logger.performance.test.ts NOT FOUND"
fi

echo ""
echo "📊 Test Statistics:"
echo "-------------------"
formatter_tests=$(grep -c "test('" tests/core/Formatter.test.ts 2>/dev/null || echo "0")
logger_tests=$(grep -c "test('" tests/core/Logger.performance.test.ts 2>/dev/null || echo "0")
total_tests=$((formatter_tests + logger_tests))

echo "Formatter tests: $formatter_tests"
echo "Logger tests: $logger_tests"
echo "Total new tests: $total_tests"

echo ""
echo "📄 Documentation files:"
echo "----------------------"
[ -f "TEST_COVERAGE_REPORT.md" ] && echo "✅ TEST_COVERAGE_REPORT.md" || echo "❌ TEST_COVERAGE_REPORT.md missing"
[ -f "TESTING_QUICK_START.md" ] && echo "✅ TESTING_QUICK_START.md" || echo "❌ TESTING_QUICK_START.md missing"

echo ""
echo "🚀 Next steps:"
echo "-------------"
echo "1. Run: npm install (if not already done)"
echo "2. Run: npm test"
echo "3. Review coverage: npm test -- --coverage"
echo ""