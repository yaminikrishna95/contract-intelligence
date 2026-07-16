import json
import time
from datetime import datetime
from pathlib import Path
from dotenv import load_dotenv
from anthropic import (
    Anthropic,
    RateLimitError,
    APIConnectionError,
    APIStatusError,
)
from schemas import Contract

load_dotenv()
client = Anthropic()

MAX_ATTEMPTS = 3

PROJECT_ROOT = Path(__file__).parent.parent
DATA_DIR = PROJECT_ROOT / "data" / "samples"
PROMPT_PATH = PROJECT_ROOT / "pipeline" / "prompts" / "extraction_v2.txt"
OUTPUT_DIR = PROJECT_ROOT / "examples"
REVIEW_DIR = PROJECT_ROOT / "reviews" / "review_needed"
LOGS_DIR = PROJECT_ROOT / "logs"

OUTPUT_DIR.mkdir(exist_ok=True)
LOGS_DIR.mkdir(exist_ok=True)
REVIEW_DIR.mkdir(exist_ok=True)


def extract_contract(contract_text: str) -> tuple[Contract, dict]:
    """Extract structured data from contract text. Returns (contract, usage_dict)."""
    prompt_template = PROMPT_PATH.read_text()
    prompt = prompt_template.replace("{contract_text}", contract_text)
    
    extraction_tool = {
        "name": "save_contract",
        "description": "Save the structured contract data extracted from the document",
        "input_schema": Contract.model_json_schema()
    }
    
    response = client.messages.create(
        model="claude-haiku-4-5",
        max_tokens=2048,
        temperature=0.0,
        system="You are an extractor of structured data from contracts.",
        tools=[extraction_tool],
        tool_choice={"type": "tool", "name": "save_contract"},
        messages=[{"role": "user", "content": prompt}]
    )
    
    tool_use_block = response.content[0]
    extracted_dict = tool_use_block.input
    contract = Contract.model_validate(extracted_dict)
    
    usage = {
        "input_tokens": response.usage.input_tokens,
        "output_tokens": response.usage.output_tokens,
    }
    return contract, usage


def validate_input(text: str) -> tuple[bool, str]:
    """Returns (is_valid, reason)."""
    if not text.strip():
        return False, "empty contract text"
    if len(text) < 100:
        return False, "text too short — likely not a real contract"
    if len(text) > 100000:
        return False, "text too long — would exceed context window"
    return True, ""


def log_event(log_file: Path, **fields):
    """Append a JSON record to the log file (JSONL format)."""
    record = {
        "timestamp": datetime.now().isoformat(),
        **fields,
    }
    with open(log_file, "a", encoding="utf-8") as f:
        f.write(json.dumps(record) + "\n")

def needs_review(contract: Contract) -> tuple[bool, str]:
    """Decide if the extracted contract needs human review.
    
    Returns (flagged, reason). Flagged if ANY of:
    - agreement_type is "other"
    - 3 or more fields are None
    - any party name contains a placeholder string
    """
    # Check 1: agreement_type is "other" → model couldn't classify
    if contract.agreement_type == "other":
        return True, "agreement_type is 'other'"
    
    # Check 2: too many null fields → mostly blank extraction
    null_count = sum(
        1 for value in contract.model_dump().values()
        if value is None
    )
    if null_count >= 1:
        return True, f"{null_count} fields are null — extraction mostly blank"
    
    # Check 3: any party name looks like a placeholder
    placeholder_patterns = ["<UNKNOWN>", "N/A", "unknown", "Not specified", "[", "TBD"]
    for party in contract.parties:
        for pattern in placeholder_patterns:
            if pattern.lower() in party.name.lower():
                return True, f"party name contains placeholder: '{party.name}'"
    
    # No flags fired — clean extraction
    return False, ""


def extract_all_contracts():
    """Run extraction on every .txt file in data/samples/ and save each output."""
    txt_files = sorted(DATA_DIR.glob("*.txt"))
    
    if not txt_files:
        print(f"No .txt files found in {DATA_DIR}")
        return
    
    # Generate a unique log file path for this run
    run_timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    log_file = LOGS_DIR / f"extraction_run_{run_timestamp}.jsonl"
    
    print(f"Found {len(txt_files)} contracts to process.")
    print(f"Logging to: {log_file.relative_to(PROJECT_ROOT)}\n")
    
    for txt_file in txt_files:
        contract_name = txt_file.stem
        
        try:
            text = txt_file.read_text(encoding="utf-8")
        except Exception as e:
            print(f"❌ {contract_name} → could not read file: {e}")
            log_event(
                log_file,
                contract=contract_name,
                status="failed",
                reason=f"file read error: {type(e).__name__}: {e}",
            )
            continue
        
        # Validate before retry loop
        is_valid, reason = validate_input(text)
        if not is_valid:
            print(f"⚠️  {contract_name} → skipped: {reason}")
            log_event(
                log_file,
                contract=contract_name,
                status="skipped",
                reason=reason,
            )
            continue
        
        # Retry loop for API call
        success = False
        last_error = ""
        
        for attempt in range(MAX_ATTEMPTS):
            try:
                start = time.time()
                result, usage = extract_contract(text)
                duration_ms = int((time.time() - start) * 1000)

                success = True
                flagged, review_reason = needs_review(result)
                if flagged:
                   output_path = REVIEW_DIR / f"{contract_name}_output.json"
                   print(f"⚠️  {contract_name} → flagged for review: {review_reason}")
                else:
                    output_path = OUTPUT_DIR / f"{contract_name}_output.json"
                    print(f"✅ {contract_name} → {output_path.relative_to(PROJECT_ROOT)}")
                output_path.write_text(result.model_dump_json(indent=2)) 

                log_event(
                    log_file,
                    contract=contract_name,
                    status="success",
                    reason="",
                    duration_ms=duration_ms,
                    input_tokens=usage["input_tokens"],
                    output_tokens=usage["output_tokens"],
                    needs_review=flagged,
                    review_reason=review_reason
                )
                
                break
            
            except (RateLimitError, APIConnectionError) as e:
                last_error = f"{type(e).__name__}: {e}"
                print(f"Transient error (attempt {attempt + 1}/{MAX_ATTEMPTS}): {e}")
                if attempt < MAX_ATTEMPTS - 1:
                    time.sleep(2 ** attempt)
            
            except APIStatusError as e:
                last_error = f"APIStatusError {e.status_code}: {e}"
                print(f"API Status Error (HTTP {e.status_code}) on attempt {attempt + 1}")
                break
        
        if not success:
            print(f"❌ FAILURE: All {MAX_ATTEMPTS} attempts exhausted for {contract_name}.")
            log_event(
                log_file,
                contract=contract_name,
                status="failed",
                reason=last_error or "all retries exhausted",
            )


if __name__ == "__main__":
    extract_all_contracts()