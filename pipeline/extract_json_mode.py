import json
from pathlib import Path
from dotenv import load_dotenv
from anthropic import Anthropic
from schemas import Contract
from pydantic import ValidationError 
import json

load_dotenv()
client = Anthropic()

PROJECT_ROOT = Path(__file__).parent.parent
DATA_DIR = PROJECT_ROOT / "data" / "samples"
PROMPT_PATH = PROJECT_ROOT / "pipeline" / "prompts" / "extraction_json_v1.txt"
OUTPUT_DIR = PROJECT_ROOT / "examples"
OUTPUT_DIR.mkdir(exist_ok=True)


def extract_contract_json_mode(contract_text: str) -> Contract:
    """Extract structured data using JSON mode (no tool use)."""
    prompt_template = PROMPT_PATH.read_text()
    schema_json = json.dumps(Contract.model_json_schema(), indent=2)
    prompt = (
        prompt_template
        .replace("{contract_text}", contract_text)
        .replace("{schema}", schema_json)
    )

    
    response = client.messages.create(
        model="claude-haiku-4-5",
        max_tokens=2048,
        temperature=0.0,
        messages=[{"role": "user", "content": prompt}]
    )
    
    raw_text = response.content[0].text
    # Strip markdown code fences if present (Claude sometimes wraps in ```json ... ```)
    cleaned = raw_text.strip()
    
    if cleaned.startswith("```"):
        cleaned = cleaned.split("```")[1]
        if cleaned.startswith("json"):
            cleaned = cleaned[4:]
        cleaned = cleaned.strip()
    
    extracted_dict = json.loads(cleaned)
    contract = Contract.model_validate(extracted_dict)
    return contract


def extract_all_contracts_json_mode():
    """Run extraction on every .txt file in data/samples/ and save each output."""
    txt_files = sorted(DATA_DIR.glob("*.txt"))
    
    if not txt_files:
        print(f"No .txt files found in {DATA_DIR}")
        return
    
    print(f"Found {len(txt_files)} contracts to process.\n")
    
    for txt_file in txt_files:
        contract_name = txt_file.stem
        try:
            text = txt_file.read_text(encoding="utf-8")
            result = extract_contract_json_mode(text)
            
            output_path = OUTPUT_DIR / "json_mode" /f"{contract_name}_output.json"
            output_path.write_text(result.model_dump_json(indent=2))
            
            print(f"✅ {contract_name} → {output_path.relative_to(PROJECT_ROOT)}")
        except json.JSONDecodeError as e:
            print(f"❌ {contract_name} → JSON parse failed: {e}")
        except ValidationError as e:
            print(f"❌ {contract_name} → Pydantic validation failed: {e}")
        except Exception as e:
            print(f"❌ {contract_name} → {type(e).__name__}: {e}")



if __name__ == "__main__":
    extract_all_contracts_json_mode()