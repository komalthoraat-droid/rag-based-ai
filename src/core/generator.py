import requests
import json
from src.monitoring.logger import logger

class LLMGenerator:
    def __init__(self, model="llama3.2"):
        self.model = model
        self.url = "http://localhost:11434/api/generate"

    def generate(self, prompt, system_prompt=None, stream=False):
        payload = {
            "model": self.model,
            "prompt": prompt,
            "stream": stream
        }
        if system_prompt:
            payload["system"] = system_prompt
            
        try:
            if stream:
                return self._stream_response(payload)
            else:
                response = requests.post(self.url, json=payload)
                response.raise_for_status()
                return response.json().get("response", "")
        except Exception as e:
            logger.error(f"Error calling LLM: {e}")
            return f"Error: {e}"

    def _stream_response(self, payload):
        response = requests.post(self.url, json=payload, stream=True)
        for line in response.iter_lines():
            if line:
                chunk = json.loads(line)
                yield chunk.get("response", "")
                if chunk.get("done"):
                    break

generator = LLMGenerator()
