# Running PE Assistant Tests with Color Output

## Best Commands

### 1. Full Suite with Color (Recommended)
```bash
docker exec faraday-ai-app-1 pytest tests/physical_education/ -v --color=yes --tb=short
```

### 2. With Color and Max Failures
```bash
docker exec faraday-ai-app-1 pytest tests/physical_education/ -v --color=yes --tb=short --maxfail=10
```

### 3. Quick Summary with Color
```bash
docker exec faraday-ai-app-1 pytest tests/physical_education/ -v --color=yes
```

### 4. Full Suite with Timeout (for hanging tests)
```bash
timeout 300 docker exec faraday-ai-app-1 pytest tests/physical_education/ -v --color=yes -k "not websocket" --maxfail=20
```

### 5. Skip Multiple Problematic Tests
```bash
docker exec faraday-ai-app-1 pytest tests/physical_education/ -v --color=yes -k "not websocket and not integration" --maxfail=10
```

### 6. Run Specific Test File Only
```bash
docker exec faraday-ai-app-1 pytest tests/physical_education/test_pe_service.py -v --color=yes
```

---

## Get Test Count
```bash
docker exec faraday-ai-app-1 pytest tests/physical_education/ --collect-only -q -k "not websocket"
```

---

## Recommended Command for Status Update

```bash
docker exec faraday-ai-app-1 pytest tests/physical_education/ -v --color=yes -k "not websocket" --tb=short --maxfail=10 2>&1 | tee pe_tests_output.txt && tail -50 pe_tests_output.txt
```

This will:
- Show colored output
- Skip websocket tests (prevents hanging)
- Stop after 10 failures
- Save to file
- Show last 50 lines

