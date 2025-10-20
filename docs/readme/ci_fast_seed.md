## CI Fast Seed Validation

Use fast seed validation to gate merges with a quick health check of Phase 1 and basic later-phase integrity.

### What it does
- Skips heavy phases using `SKIP_PHASE_2..11`
- Caps students via `MAX_TOTAL_STUDENTS` (default 1000) and fixes RNG via `SEED_RNG` (default 1234)
- Applies unique/performance indexes
- Runs `post_seed_validation.py` (structure + distribution + orphan checks + later-phase presence checks)

### Local
```bash
# uses Azure Postgres by default (from run.sh). Override if needed:
DATABASE_URL=postgresql://<user>:<pass>@<host>:5432/postgres?sslmode=require bash ./run_fast_seed_validation.sh
```

### CI example (GitHub Actions)
```yaml
- name: Fast seed validation
  env:
    DATABASE_URL: postgresql://faraday_admin:CodaMoeLuna31@faraday-ai-db.postgres.database.azure.com:5432/postgres?sslmode=require
    SKIP_PHASE_2: true
    SKIP_PHASE_3: true
    SKIP_PHASE_4: true
    SKIP_PHASE_5: true
    SKIP_PHASE_6: true
    SKIP_PHASE_7: true
    SKIP_PHASE_8: true
    SKIP_PHASE_9: true
    SKIP_PHASE_10: true
    SKIP_PHASE_11: true
    MAX_TOTAL_STUDENTS: 1000
    SEED_RNG: 1234
  run: bash ./run_fast_seed_validation.sh
```

If validation fails, the step exits non-zero and the pipeline fails.


