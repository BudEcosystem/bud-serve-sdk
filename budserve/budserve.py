import os
from typing import Mapping
from httpx import URL, Client, Timeout
from openai import NotGiven, OpenAI

class BudServe(OpenAI):

    def __init__(self,
                 api_key: str | None = None, 
                 base_url: str | URL | None = None
                ) -> None:
        
        if api_key is None:
            api_key = os.environ.get("BUDSERVE_API_KEY", None)
        if api_key is None:
            raise Exception(
                "The api_key client option must be set either by passing api_key to the client or by setting the BUDSERVE_API_KEY environment variable"
            )
        
        super().__init__(
            api_key=api_key, 
            base_url=base_url, 
            default_headers={'api-key': api_key})