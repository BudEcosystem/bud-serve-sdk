import os
from guidance.models._model import Chat, Instruct
from guidance.models.transformers._transformers import TransformersTokenizer

from transformers import AutoTokenizer

from .guidance_engine.budserve_engine import BudServe, BudServeEngine


class BudServeClient(BudServe):
    def __init__(
        self,
        model,
        tokenizer=None,
        echo=True,
        api_key=None,
        max_streaming_tokens=1000,
        timeout=0.5,
        compute_log_probs=False,
        engine_class=None,
        **kwargs,
    ):
        """
        Build a new BudServe model object that represents a model in a given state.
        """
        if tokenizer is not None:
            tokenizer = AutoTokenizer.from_pretrained(model)

        tokenizer = TransformersTokenizer(
            model=model, tokenizer=tokenizer, ignore_bos_token=True
        )

        # Default base_url is the together.ai endpoint
        if not "base_url" in kwargs:
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

        if engine_class is None:
            engine_map = {
                BudServeCompletion: BudServeEngine,
                BudServeInstruct: BudServeEngine,
                BudServeChat: BudServeEngine,
                BudServe: BudServeEngine,
            }
            for k in engine_map:
                if issubclass(self.__class__, k):
                    engine_class = engine_map[k]
                    break

        super().__init__(
            model,
            tokenizer,
            echo,
            api_key,
            max_streaming_tokens,
            timeout,
            compute_log_probs,
            **kwargs,
        )

class BudServeCompletion(BudServeClient):
    pass


class BudServeInstruct(BudServeClient, Instruct):

    def get_role_start(self, name):
        if name == "instruction":
            return "<|im_start|>user\n"
        else:
            raise Exception(
                f"The model does not know about the {name} role type!"
            )

    def get_role_end(self, name):
        if name == "instruction":
            return "<|im_end|>"
        else:
            raise Exception(
                f"The model does not know about the {name} role type!"
            )


class BudServeChat(BudServeClient, Chat):
    pass
