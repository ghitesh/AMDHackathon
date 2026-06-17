import json
import openai

import httpx
import asyncio
import architecture_schema  # Only importingimport architecture_schema
import generate_ppt

# Configuration for local vLLM
VLLM_ENDPOINT = "http://localhost:8000/v1/chat/completions"

    
def get_system_prompt():
    """Defines the system instruction using only the Architecture schema."""
    schema = architecture_schema.Architecture.model_json_schema()
    print(json.dumps(schema))
    return f"""
    You are an expert AWS architecture assistant. 
    Generate a structured JSON output representing the requested architecture.
    Ensure the output is valid JSON only and does not contain any additional comment or string.
    In the response json, keep "service" value as close to AWS service/component name as possible. For example Label: Web Server 1, service=EC2
    You must strictly follow this JSON schema and directly json:
    {json.dumps(schema)}
    """

async def generate_architecture(prompt: str):
    """Calls the local vLLM to generate the architecture JSON."""
    async with httpx.AsyncClient() as client:
        response = await client.post(
            VLLM_ENDPOINT,
            json={
                "model": "unsloth/Phi-3.5-mini-Instruct",
                "messages": [
                    {"role": "system", "content": get_system_prompt()},
                    {"role": "user", "content": prompt}
                ],
                "extra_body": {"response_format": {"type": "json_object"}}
            },
            timeout=60.0
        )
        data = response.json()
        #print(data['choices'][0]['message']['content'])
        json_res = data['choices'][0]['message']['content'].strip().strip("`")
        if json_res.lower().startswith("json"):
            json_res = json_res[4:].strip()
        ##print(json_res)
        return json.loads(json_res)

def validate_and_save(architecture_dict):
    """Validates output against Architecture model and returns object."""
    # This validates the LLM output against your Pydantic schema
    return architecture_schema.Architecture.model_validate(architecture_dict)

# Integration logic
if __name__ == "__main__":
    user_input = "Create a 2-tier AWS architecture with an ELB, 2 EC2 instances, and an RDS instance."
    # 1. Generate
    arch_json = asyncio.run(generate_architecture(user_input))
    
    # 2. Validate
    # print(arch_json)
    # validated_arch = validate_and_save(arch_json)
    
    # 3. Save for generate_ppt.p
    # print(arch_json)# arch_json)
    with open("architecture_output.json", "w") as f:
        json.dump(arch_json, f)
    
    print("Architecture JSON generated and validated successfully.")

    # 4. Call generate_ppt.py
    generate_ppt.call_generate_ppt(inputfile="architecture_output.json",outputfile="outfile.pptx")
        