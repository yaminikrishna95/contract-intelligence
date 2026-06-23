import json
from pathlib import Path
from dotenv import load_dotenv
from anthropic import Anthropic
from schemas import Contract

load_dotenv()
client = Anthropic()

PROJECT_ROOT = Path(__file__).parent.parent
DATA_DIR = PROJECT_ROOT / "data" / "samples"
PROMPT_PATH = PROJECT_ROOT / "pipeline" / "prompts" / "extraction_v2.txt"
OUTPUT_DIR = PROJECT_ROOT / "examples"
OUTPUT_DIR.mkdir(exist_ok=True)


def extract_contract(contract_text: str) -> Contract:
    """Extract structured data from contract text using Claude tool use."""
    prompt_template = PROMPT_PATH.read_text()
    prompt = prompt_template.replace("{contract_text}", contract_text)
    
    extraction_tool = {
        "name": "save_contract",
        "description": "Save the structured contract data extracted from the documåçent",
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
    return contract


def extract_all_contracts():
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
            result = extract_contract(text)
            
            output_path = OUTPUT_DIR / f"{contract_name}_output.json"
            output_path.write_text(result.model_dump_json(indent=2))
            
            print(f"✅ {contract_name} → {output_path.relative_to(PROJECT_ROOT)}")
        except Exception as e:
            print(f"❌ {contract_name} → error: {type(e).__name__}: {e}")


if __name__ == "__main__":
    extract_all_contracts()