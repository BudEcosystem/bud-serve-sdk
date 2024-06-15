# Bud Serve Python SDK

A client package to directly integrate Bud Serve engine to your python application. The package support different prompting libraries like Guidance, langchain etc.

### Installation

```
pip install git+https://github.com/BudEcosystem/bud-serve-sdk.git
```

### Supported integrations:

- [X] Guidance
- [ ] LangChain
- [ ] LlamaIndex
- [ ] Haystack
- [ ] LMQL

### Guidance example

Add the API key to the enviornament

```
export BUDSERVE_API_KEY=XXXXXXXX
```
Sample code to connect to bud serve remote server using guidance

```
from guidance import gen, user, system, assistant
from budserve.models.guidance import BudServeClient

llama2 = BudServeClient("meta-llama/Llama-2-7b-chat-hf", echo=False, base_url="http://localhost9000/v1")

with user():
    llama2 += f'what is your name? '

with assistant():
    llama2 += gen("answer", stop='.')


print(llama2["answer"])

```