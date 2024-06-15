from guidance import gen, user, system, assistant
from budserve.models.guidance import BudServeClient

llama2 = BudServeClient("meta-llama/Llama-2-7b-hf", echo=False, base_url="http://20.51.203.32:9000/v1")

with user():
    llama2 += f'what is your name? '

with assistant():
    llama2 += gen("answer", stop='.')

print(llama2["answer"])
