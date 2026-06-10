from openai import OpenAI


class LLMClient:

    def __init__(self, base_url, api_key="EMPTY"):
        self.client = OpenAI(
            base_url=base_url,
            api_key=api_key
        )

    def generate(self, prompt):

        response = self.client.chat.completions.create(
            model="aws-architect",
            messages=[
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            temperature=0.1
        )

        return response.choices[0].message.content
