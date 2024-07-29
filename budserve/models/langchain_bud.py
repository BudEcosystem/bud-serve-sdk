from typing import Any, Dict, Iterator, List, Optional
import requests
from langchain_core.callbacks.manager import CallbackManagerForLLMRun
from langchain_core.language_models.llms import LLM
from langchain_core.outputs import GenerationChunk

class BUD(LLM):
    
    base_url = ""
    model_name = ""
    api_key = ""
    max_tokens = 0
    
    def __init__(self, bud_base_url,model_name,api_key,max_tokens=512):
        super().__init__() 
        self.base_url = f"{bud_base_url}/chat/completions"
        self.model_name = model_name
        self.api_key = api_key
        self.max_tokens = max_tokens

    def _call(
        self,
        prompt: str,
        stop: Optional[List[str]] 
        = None,
        run_manager: Optional[CallbackManagerForLLMRun] = None,
        **kwargs: Any,
    ) -> str:
        response = self.fetch_completion_from_api(prompt)
        if stop is not None:
            raise ValueError("stop kwargs are not permitted.")
        return response


    def _stream(
        self,
        prompt: str,
        stop: Optional[List[str]] = None,
        run_manager: Optional[CallbackManagerForLLMRun] = None,
        **kwargs: Any,
    ) -> Iterator[GenerationChunk]:
        headers = {'Content-Type': 'application/json', 'api-key':self.api_key}
        payload = {
            "model": self.model_name,
            "max_tokens": self.max_tokens,
            "messages": [{"role": "user", "content": prompt}],
            "stream": True,
            "engine": "budserve"
        }
        response_iter = requests.post(self.base_url, json=payload, headers=headers, stream=True)
        for chunk in response_iter.iter_lines(decode_unicode=False, delimiter=b"\n\n"):
            chunk = chunk.strip()
            if not chunk:
                continue
            chunk = chunk.decode("utf-8").lstrip("data: ")
            if chunk != "[DONE]":
                yield GenerationChunk(text= chunk+'\n')

    @property
    def _identifying_params(self) -> Dict[str, Any]:
        """Return a dictionary of identifying parameters."""
        return {
            "model_name": "CustomChatModel",
        }

    @property
    def _llm_type(self) -> str:
        """Get the type of language model used by this chat model. Used for logging purposes only."""
        return "custom"

    def fetch_completion_from_api(self, prompt: str) -> str:
        headers = {'Content-Type': 'application/json', 'api-key':self.api_key}
        payload = {
            "model": self.model_name,
            "max_tokens": self.max_tokens,
            "messages": [{"role": "user", "content": prompt}],
            "engine": "budserve"
        }
        try:
            response = requests.post(self.base_url, json=payload, headers=headers)
            response.raise_for_status()
            return response.json().get('choices', [])[0]['message']['content']
        except requests.exceptions.RequestException as e:
            print(f"Error fetching completion from API: {e}")
            return ""