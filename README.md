# Bud Serve Python SDK

A client package to directly integrate Bud Serve engine to your python application. The package support different prompting libraries like Guidance, langchain etc.

### Installation

```bash
pip install git+https://github.com/BudEcosystem/bud-serve-sdk.git
```

### Usage

The inference engine can be accessed via OpenAI api format and the options available in the OpenAI chat and completion can be used from our client.

```python
from budserve import BudServe

client = BudServe(base_url="http://x.x.x.x:xxx/v1")

completion = client.chat.completions.create(
    model="meta-llama/Llama-2-7b-chat-hf",
    messages=[{"role": "user", "content": "write an essay about history of cricket"}],
    max_tokens=200
)

print(completion.choices[0].message.content)
```
You will need add the api key, `BUDSERVE_API_KEY=XXXXXXXX` in your env to authenticate.


### Streaming responses:

The streaming response support is provided using Server Side Events.

```python
from budserve import BudServe

client = BudServe(base_url="http://x.x.x.x:xxx/v1")

stream = client.chat.completions.create(
    model="meta-llama/Llama-2-7b-chat-hf",
    messages=[{"role": "user", "content": "write an essay about history of cricket"}],
    stream=True,
    max_tokens=200
)

for chunk in stream:
    print(chunk.choices[0].delta.content or "", end="", flush=True)
```



## Supported integrations:

- [X] Guidance
- [ ] LangChain
- [ ] LlamaIndex
- [ ] Haystack
- [ ] LMQL

### Guidance example

Add the API key to the enviornament

```bash
export BUDSERVE_API_KEY=XXXXXXXX
```
Sample code to connect to bud serve remote server using guidance

```python
from guidance import gen, user, system, assistant
from budserve.models.guidance import BudServeClient

llama2 = BudServeClient("meta-llama/Llama-2-7b-chat-hf", echo=False, base_url="http://localhost9000/v1")

with user():
    llama2 += f'what is your name? '

with assistant():
    llama2 += gen("answer", stop='.')


print(llama2["answer"])

```