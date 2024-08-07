from guidance import gen, user, system, assistant
from budserve.models.guidance import BudServeClient

llama2 = BudServeClient("meta-llama/Llama-2-7b-chat-hf", echo=False, base_url="http://x.x.x.x:xxx/v1")

with user():
    llama2 += f'what is your name? '

with assistant():
    llama2 += gen("answer", stop='.')

print(llama2["answer"])
