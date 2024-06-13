from openai import OpenAI
import os
from dotenv import load_dotenv

load_dotenv()

class OpenAIConfig:
    def __init__(self):
        self.MODEL = 'gpt-4o'
        self.client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

    def get_data(self,prompt):
        completion = self.client.chat.completions.create(
        model=self.MODEL,
        
        messages=[
                {"role": "system", "content": "You are a professional web scraper, all the output should be in a nice json format."},
                {"role": "user", "content": [
                    {"type": "text", "text": f'extract the email of the company from the given html and return the output as json: \n{prompt}'},
                ]}
            ],
        temperature=0.0,
        )

        return completion.choices[0].message.content