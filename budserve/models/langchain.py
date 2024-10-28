import os
from typing import Any, Dict, Iterator, List, Optional
import requests
from langchain_core.callbacks.manager import CallbackManagerForLLMRun
from langchain_core.language_models import LLM
from langchain_core.outputs import GenerationChunk
from pydantic import Field


class BudServeClient(LLM):
    base_url: str = Field(default="")
    model_name: str = Field(default="")
    api_key: str = Field(default="")
    max_tokens: int = Field(default=0)
    
    def __init__(self, base_url, model_name, api_key, max_tokens=512):
        super().__init__() 
        self.base_url = f"{base_url}/chat/completions"
        self.model_name = model_name
        self.api_key = api_key
        self.max_tokens = max_tokens

        # Default base_url is the together.ai endpoint
        if base_url is None:
            raise Exception(
                "The base_url is required to connect to the correct server. (eg: http://x.x.x.x:8000/v1)"
            )
        # BudServe uses BUDSERVE_API_KEY env value instead of OPENAI_API_KEY
        # We pass explicitly to avoid OpenAI class complaining about a missing key
        if api_key is None:
            api_key = os.environ.get("BUDSERVE_API_KEY", None)
        if api_key is None:
            raise Exception(
                "The api_key client option must be set either by passing api_key to the client or by setting the BUDSERVE_API_KEY environment variable"
            )

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
            # "engine": "budserve"
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
        return "budserve"

    def fetch_completion_from_api(self, prompt: str) -> str:
        headers = {'Content-Type': 'application/json', 'api-key':self.api_key}
        payload = {
            "model": self.model_name,
            "max_tokens": self.max_tokens,
            "messages": [{"role": "user", "content": prompt}],
            # "engine": "budserve"
        }
        try:
            response = requests.post(self.base_url, json=payload, headers=headers)
            response.raise_for_status()
            return response.json().get('choices', [])[0]['message']['content']
        except requests.exceptions.RequestException as e:
            print(f"Error fetching completion from API: {e}")
            return ""
