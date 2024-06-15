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
    

    def _generator(self, prompt: bytes, temperature: float):
        assert isinstance(prompt, bytes)
        # if self.model_name in self._completion_models:
        return self._generator_completion(prompt, temperature)
        # else:
            # Otherwise we are in a chat context
            # return self._generator_chat(prompt, temperature)
            # print("Not implemented")


class BudServe(Grammarless):

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