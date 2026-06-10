import json

from models.llm_client import LLMClient


class ArchitectureAgent:

    def __init__(self, llm):
        self.llm = llm

    def generate_architecture(
        self,
        user_prompt,
        rag_context
    ):

        prompt = f"""
You are an AWS Solutions Architect.

Generate ONLY JSON.

Context:
{rag_context}

User Request:
{user_prompt}

Output Schema:

{{
  "title":"",
  "description":"",
  "nodes":[
    {{
      "id":"",
      "service":"",
      "label":""
    }}
  ],
  "edges":[
    {{
      "source":"",
      "target":"",
      "relation":""
    }}
  ]
}}
"""

        response = self.llm.generate(prompt)

        return json.loads(response)
