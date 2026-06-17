import openai
import json
import subprocess
import architecture_schema
import diagram_model

# 1. Load schema context dynamically
def get_schema_context():
    # Extracts relevant schema documentation/types as string
    # Assumes your files have well-defined classes/docstrings
    schema_info = f"Schema Reference:\n{architecture_schema.__doc__ or ''}\n"
    schema_info += f"Model Reference:\n{diagram_model.__doc__ or ''}"
    return schema_info

client = openai.OpenAI(base_url="http://localhost:8001/v1", api_key="ignored")

def run_agent(requirement, output_filename):
    schema_context = get_schema_context()
    
    # 2. Inject schema into the system prompt
    system_prompt = f"""You are an AWS Architecture AI. 
    You must strictly adhere to the following schema for all outputs:
    {schema_context}
    Respond ONLY with a JSON object that satisfies this schema."""
    
    response = client.chat.completions.create(
        model="phi-3.5-mini",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"Requirements: {requirement}"}
        ],
        extra_body={"response_format": {"type": "json_object"}}
    )
    
    # 3. Validate and Save
    try:
        arch_data = json.loads(response.choices[0].message.content)
        # Optional: Add Pydantic validation here using architecture_schema.Architecture.model_validate(arch_data)
        
        json_path = "current_architecture.json"
        with open(json_path, 'w') as f:
            json.dump(arch_data, f)
            
        # 4. Invoke PPT Generator
        subprocess.run(["python", "generate_ppt.py", "--input", json_path, "--output", output_filename], check=True)
        print(f"PPT successfully generated: {output_filename}")
        
    except Exception as e:
        print(f"Error during agent execution: {e}")

# Usage
run_agent("A high-availability VPC with two public subnets and one private RDS instance.", "my_architecture.pptx")
 
