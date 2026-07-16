"""Validate all expected_outputs JSON files against the Contract schema."""
import json
import sys
from pathlib import Path

# Hardcode the pipeline directory to be safe
PIPELINE_DIR = Path("/Users/yamini/contract-intelligence/contract-intelligence/pipeline")
EXPECTED_DIR = Path("/Users/yamini/contract-intelligence/contract-intelligence/expected_outputs")

sys.path.insert(0, str(PIPELINE_DIR))

from schemas import Contract

files = sorted(EXPECTED_DIR.glob("contract_*_expected.json"))

if not files:
    print(f"No files found in {EXPECTED_DIR}")
    sys.exit(1)

print(f"Validating {len(files)} label files against Contract schema...\n")

pass_count = 0
fail_count = 0

for f in files:
    try:
        data = json.loads(f.read_text())
        Contract.model_validate(data)
        print(f"✅ {f.name}")
        pass_count += 1
    except json.JSONDecodeError as e:
        print(f"❌ {f.name} — invalid JSON: {e}")
        fail_count += 1
    except Exception as e:
        error_msg = str(e)[:250]
        print(f"❌ {f.name} — schema validation failed:\n   {error_msg}\n")
        fail_count += 1

print(f"\n{pass_count}/{len(files)} passed")
if fail_count > 0:
    print(f"⚠️  {fail_count} failed — fix and re-run")
    sys.exit(1)