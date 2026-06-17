import json
import httpx
import asyncio
from architecture_schema import Architecture  # Only importing architecture_schema

# Configuration for local vLLM
VLLM_ENDPOINT = "http://localhost:8001/v1/chat/completions"

def get_system_prompt():
    """Defines the system instruction using only the Architecture schema."""
    schema = Architecture.model_json_schema()
    return f"""
    You are an expert AWS architecture assistant. 
    Generate a structured JSON output representing the requested architecture.
    You must strictly follow this JSON schema:
    {json.dumps(schema)}
    
    Ensure the output is valid JSON only.
    """

async def generate_architecture(prompt: str):
    """Calls the local vLLM to generate the architecture JSON."""
    async with httpx.AsyncClient() as client:
        response = await client.post(
            VLLM_ENDPOINT,
            json={
                "model": "your-model-name",
                "messages": [
                    {"role": "system", "content": get_system_prompt()},
                    {"role": "user", "content": prompt}
                ],
                "extra_body": {"response_format": {"type": "json_object"}}
            },
            timeout=60.0
        )
        data = response.json()
        return json.loads(data['choices'][0]['message']['content'])

def validate_and_save(architecture_dict):
    """Validates output against Architecture model and returns object."""
    # This validates the LLM output against your Pydantic schema
    return Architecture.model_validate(architecture_dict)

# Integration logic
if __name__ == "__main__":
    user_input = "Create a 2-tier AWS architecture with an ELB, 2 EC2 instances, and an RDS instance."
    
    # 1. Generate
    arch_json = asyncio.run(generate_architecture(user_input))
    
    # 2. Validate
    validated_arch = validate_and_save(arch_json)
    
    # 3. Save for generate_ppt.py
    with open("architecture_output.json", "w") as f:
        json.dump(validated_arch.model_dump(), f)
    
    print("Architecture JSON generated and validated successfully.")
