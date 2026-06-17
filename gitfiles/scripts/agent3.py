import openai
import json
import subprocess
import os

# 1. Configuration
VLLM_ENDPOINT = "http://localhost:8001/v1"
MODEL_NAME = "phi-3.5-mini" # Ensure this matches your running vLLM model
OUTPUT_PPT_FILE = "generated_architecture.pptx"
TEMP_JSON_FILE = "architecture_output.json"

# Mock schema loader (Update with your actual import path)
# From your file history, these define your graph structure
import architecture_schema 
import diagram_model

def get_schema_context():
    """Builds a schema prompt from your defined models."""
    return f"""
    Schema Definition:
    Containers: {architecture_schema.__doc__ or 'Nodes arranged in hierarchy (Region -> VPC -> AZ -> Subnet)'}
    Node Types: {diagram_model.__doc__ or 'AWS Service nodes (EKS, MSK, Aurora, etc.)'}
    Ensure output follows the JSON structure: {{ "title": str, "description": str, "containers": [...], "nodes": [...], "edges": [...] }}
    """

def run_agent(user_requirement):
    client = openai.OpenAI(base_url=VLLM_ENDPOINT, api_key="local-vllm")
    
    # 2. Prepare Prompt
    system_prompt = f"You are an AWS Architect. Generate strict JSON architecture based on this schema:\n{get_schema_context()}"
    
    print(f"Generating architecture for: {user_requirement}...")
    
    # 3. Call vLLM Model
    try:
        response = client.chat.completions.create(
            model=MODEL_NAME,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_requirement}
            ],
            extra_body={"response_format": {"type": "json_object"}}
        )
        
        arch_json_str = response.choices[0].message.content
        arch_data = json.loads(arch_json_str)
        
        # Save to file for generator
        with open(TEMP_JSON_FILE, 'w') as f:
            json.dump(arch_data, f, indent=2)
            
        print(f"Architecture JSON saved to {TEMP_JSON_FILE}")

        # 4. Invoke PPT Generator
        print(f"Calling generate_ppt.py...")
        subprocess.run(["python", "generate_ppt.py", "--input", TEMP_JSON_FILE, "--output", OUTPUT_PPT_FILE], check=True)
        
        print(f"Successfully generated: {OUTPUT_PPT_FILE}")
        
    except Exception as e:
        print(f"Agent Pipeline Failed: {e}")

if __name__ == "__main__":
    # Example usage: passing the requirement via command line or hardcoded
    req = "Design an Active-Active Multi-Region EKS Application with MSK and Aurora."
    run_agent(req)
 
