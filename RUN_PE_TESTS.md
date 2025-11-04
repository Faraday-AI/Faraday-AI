# Running PE Assistant Tests

## ✅ Issues Fixed
- **Prometheus metrics duplication** - Fixed with try/except in `app/core/cache.py`
- **Redis not running** - Started Redis container
- **Test collection errors** - All 1120 tests now collect successfully

## Commands to Copy & Paste

### Option 1: Quick Summary (Recommended)
```bash
docker exec faraday-ai-app-1 pytest tests/physical_education/ --tb=no -v -x
```
- `-x` stops at first failure
- `-v` verbose output
- `--tb=no` no traceback to reduce output

### Option 2: Full Test Suite with Summary
```bash
docker exec faraday-ai-app-1 pytest tests/physical_education/ -v --tb=short --maxfail=5
```
- `--maxfail=5` stops after 5 failures
- Shows first 5 failures with details

### Option 3: Run Specific Test File
```bash
docker exec faraday-ai-app-1 pytest tests/physical_education/test_pe_service.py -v
```

### Option 4: Count Tests Only
```bash
docker exec faraday-ai-app-1 pytest tests/physical_education/ --collect-only -q
```

### Option 5: Run with Timeout (if hanging)
```bash
timeout 120 docker exec faraday-ai-app-1 pytest tests/physical_education/ --tb=no -q
```
- Stops after 2 minutes (120 seconds)
- Quick output only

### Option 6: Save Output to File
```bash
docker exec faraday-ai-app-1 pytest tests/physical_education/ --tb=short > pe_test_results.txt 2>&1
cat pe_test_results.txt | tail -100
```

---

## Recommended Command (Best Balance)

```bash
docker exec faraday-ai-app-1 pytest tests/physical_education/ --tb=short --maxfail=10 -v 2>&1 | tee pe_test_output.txt
```

This will:
- Show test progress in real-time
- Stop after 10 failures
- Save output to file
- Give you full details on failures

