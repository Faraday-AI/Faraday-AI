#!/usr/bin/env python3
"""Parse pytest output and count PASSED, FAILED, ERROR tests."""
import sys

# The test output provided by the user (partial)
test_output = """
[test output here]
"""

# Counters
passed = 0
failed = 0
errors = 0

# Parse the output
for line in sys.stdin:
    if 'PASSED' in line:
        passed += 1
    elif 'FAILED' in line:
        failed += 1
    elif 'ERROR' in line:
        errors += 1

print(f"PASSED: {passed}")
print(f"FAILED: {failed}")
print(f"ERROR: {errors}")
print(f"Total processed: {passed + failed + errors}")

