import json
import openai

import httpx
import asyncio
import architecture_schema  # Only importingimport architecture_schema
import argparse
import generate_ppt
import re

# Configuration for local vLLM
VLLM_ENDPOINT = "http://localhost:8000/v1/chat/completions"

def extract_json(text):
    # Regex to find everything between the first { and last }
    match = re.search(r'\{.*\}', text, re.DOTALL)
    if match:
        json_str = match.group(0)
        try:
            return json.loads(json_str)
        except json.JSONDecodeError:
            return None
    return None
    
def clean_and_parse(text):
    # Remove markdown code block markers
    cleaned_text = re.sub(r'```(?:json)?\s*|\s*```', '', text).strip()
    try:
        return json.loads(cleaned_text)
    except json.JSONDecodeError:
        # Fall back to the regex extraction if cleaning isn't enough
        return extract_json(text)
    
def get_system_prompt():
    """Defines the system instruction using only the Architecture schema."""
    schema = architecture_schema.Architecture.model_json_schema()
    #print(json.dumps(schema))
    return f"""
    You are an expert AWS architecture assistant. 
    Generate a structured JSON output representing the requested architecture.
    Format your response exactly as JSON. Output nothing else.
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
                #"model": "unsloth/Phi-3.5-mini-Instruct",
                "model": "microsoft/phi-4",
                "messages": [
                    {"role": "system", "content": get_system_prompt()},
                    {"role": "user", "content": prompt + ". Enclose architecture between AWS OR Region OR Zonal and/or VPC boundary as applicable. Return only the applicable json response without any explanations"}
                ],
                "extra_body": {"response_format": {"type": "json_object"}}
            },
            timeout=120.0
        )
        data = response.json()
        print(data['choices'][0]['message']['content'])
        json_res = clean_and_parse(data['choices'][0]['message']['content'])
        print("agent.py Line 65 json_res =",json_res)
        return json_res

def validate_and_save(architecture_dict):
    """Validates output against Architecture model and returns object."""
    # This validates the LLM output against your Pydantic schema
    return architecture_schema.Architecture.model_validate(architecture_dict)

# Integration logic
if __name__ == "__main__":

    parser = argparse.ArgumentParser(description="Describe your architecture")
    parser.add_argument("--architecture", type=str, required=True, help="The text input to print")
    
    # Parse arguments
    args = parser.parse_args()
    
    print(f"Your message is: {args.architecture}")

    user_input = args.architecture
    #user_input = "Create a 2-tier AWS architecture with an ELB, 2 EC2 instances, and an RDS instance."
    # 1. Generate
    print("1. Generating response from LLM with a timeout of 120s")
    arch_json = asyncio.run(generate_architecture(user_input))
    
    # 2. Validate
    # print(arch_json)
    # validated_arch = validate_and_save(arch_json)
    
    # 3. Save for generate_ppt.p
    # print(arch_json)# arch_json)
    print("2. Writing architecture_output.json")
    with open("architecture_output.json", "w") as f:
        json.dump(arch_json, f)
    
    print("Architecture JSON generated and validated successfully.")

    # 4. Call generate_ppt.py
    generate_ppt.call_generate_ppt(inputfile="architecture_output.json",outputfile="outfile.pptx")
        