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
- [X] LangChain
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

### Langchain example

Sample code to connect to bud serve remote server using guidance

```python

from budserve.models.langchain import BudServeClient
from langchain_core.prompts import PromptTemplate
from langchain.schema.output_parser import StrOutputParser


llm = BudServeClient(base_url="http://localhost9000/v1",
                 model_name="meta-llama/Meta-Llama-3-8B-Instruct",
                 api_key="xxxxxxxxx")

prompt_template = PromptTemplate.from_template("Tell me a joke about {topic}")

chain = prompt_template | llm | StrOutputParser()

print(chain.invoke("cat"))

```

## Tasks

We have extended the package with some off the shelf fuctions for specific task. 

### Summarization


```python
from budserve import BudServe
from budserve.tasks import Summerization

client = BudServe(base_url="x.x.x.x:xxxx/v1", model_name="microsoft/Phi-3-mini-4k-instruct")


article = "You call transcription here"

summerizer = Summerization(client=client, num_sen=3, num_words=40)
summary = summerizer.summarize_text(text=article, topic="Support call transcription")
print(summary)
```

Here are the option available to for summarization task

***client*:** BudServe client which connect with the server for inference

***num_sen:*** Required number of sentences for the summary. Default value: 4

***num_words:*** Total number of required words in the summary. Default value: 80

***topic:*** The type of content which provided for summarisation. This helps to align the model generation to specific domain. eg: Article, paper, documentation, call transcription etc
