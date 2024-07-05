import typing
from guidance.models._grammarless import Grammarless
import openai
from .grammarless import GrammarlessEngine

client_class: typing.Optional[typing.Type[openai.OpenAI]] = openai.OpenAI

class BudServeEngine(GrammarlessEngine):

    def __init__(
            self, 
            tokenizer, 
            api_key,
            max_streaming_tokens, 
            timeout, 
            compute_log_probs,
            model,
            base_url
        ):

        self.model_name = model
        self.client = client_class(base_url=base_url, api_key=api_key, default_headers={'api-key': api_key})

        super().__init__(
            tokenizer, 
            max_streaming_tokens, 
            timeout, 
            compute_log_probs)

    
    def _generator_completion(self, prompt: bytes, temperature: float):
        
        self._reset_shared_data(prompt, temperature)

        try:
            prompt_decoded = prompt.decode("utf8")
            generator = self.client.completions.create(
                model=self.model_name,
                prompt=prompt_decoded,
                max_tokens=self.max_streaming_tokens,
                n=1,
                top_p=1.0,  # TODO: this should be controllable like temp (from the grammar)
                temperature=temperature,
                stream=True,
            )
            self.metrics.engine_input_tokens += len(self.tokenizer(prompt_decoded))
        except Exception as e:
            # TODO: add retry logic, but keep token counts straight
            raise e
        
        for part in generator:
            if len(part.choices) > 0:
                chunk = part.choices[0].text or ""
            else:
                chunk = ""
            self.metrics.engine_output_tokens += len(self.tokenizer(chunk))
            yield chunk.encode("utf8")
    

    def _generator_chat(self, prompt: bytes, temperature: float):
        # find the role tags
        pos = 0
        role_end = b"<|im_end|>\n"
        messages = []
        found = True
        input_token_count = 0

        # TODO: refactor this to method on parent class? (or a util function)
        while found:
            # find the role text blocks
            found = False
            for role_name, start_bytes in (
                ("system", b"<|im_start|>system\n"),
                ("user", b"<|im_start|>user\n"),
                ("assistant", b"<|im_start|>assistant\n"),
            ):
                if prompt[pos:].startswith(start_bytes):
                    pos += len(start_bytes)
                    end_pos = prompt[pos:].find(role_end)
                    if end_pos < 0:
                        assert (
                            role_name == "assistant"
                        ), "Bad chat format! Last role before gen needs to be assistant!"
                        break
                    btext = prompt[pos : pos + end_pos]
                    pos += end_pos + len(role_end)
                    message_content: str = btext.decode("utf8")
                    input_token_count += len(self.tokenizer(message_content))
                    messages.append({"role": role_name, "content": message_content})
                    found = True
                    break

        # Add nice exception if no role tags were used in the prompt.
        # TODO: Move this somewhere more general for all chat models?
        if messages == []:
            raise ValueError(
                f"The model {self.model_name} is a Chat-based model and requires role tags in the prompt! \
            Make sure you are using guidance context managers like `with system():`, `with user():` and `with assistant():` \
            to appropriately format your guidance program for this type of model."
            )

        # Update shared data state
        self._reset_shared_data(prompt[:pos], temperature)

        # API call and response handling
        try:
            # Ideally, for the metrics we would use those returned by the
            # OpenAI API. Unfortunately, it appears that AzureAI hosted
            # models do not support returning metrics when streaming yet
            generator = self.client.chat.completions.create(
                model=self.model_name,
                messages=messages,
                max_tokens=self.max_streaming_tokens,
                n=1,
                top_p=1.0,  # TODO: this should be controllable like temp (from the grammar)
                temperature=temperature,
                stream=True,
            )
            self.metrics.engine_input_tokens += input_token_count

            for part in generator:
                if len(part.choices) > 0:
                    chunk = part.choices[0].delta.content or ""
                else:
                    chunk = ""
                encoded_chunk = chunk.encode("utf8")
                self.metrics.engine_output_tokens += len(
                    self.tokenizer(chunk)
                )
                yield encoded_chunk

        except Exception as e:
            # TODO: add retry logic, keeping mind of token counts
            raise e
        
    def _generator(self, prompt: bytes, temperature: float):
        assert isinstance(prompt, bytes)
        is_chat_model = False
        for role_name, start_bytes in (
                ("system", b"<|im_start|>system\n"),
                ("user", b"<|im_start|>user\n"),
                ("assistant", b"<|im_start|>assistant\n"),
            ):
                if prompt.startswith(start_bytes):
                    is_chat_model = True
        
        if not is_chat_model:
            return self._generator_completion(prompt, temperature)
        else:
            # Otherwise we are in a chat context
            return self._generator_chat(prompt, temperature)
            # print("Not implemented")


class BudServeGrammerless(Grammarless):

    def __init__(
        self, 
        model,
        tokenizer=None,
        echo=False,
        api_key=None,
        max_streaming_tokens=1000,
        timeout=0.5,
        compute_log_probs=False,
        base_url=None):

        super().__init__(
            engine=BudServeEngine(
                tokenizer=tokenizer,
                api_key=api_key,
                max_streaming_tokens=max_streaming_tokens,
                timeout=timeout,
                compute_log_probs=compute_log_probs,
                model=model,
                base_url=base_url
            ), 
            echo=echo)