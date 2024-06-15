from guidance import gen, user, system, assistant
from budserve.models.guidance import BudServeClient

llama2 = BudServeClient("microsoft/Phi-3-medium-4k-instruct", echo=False, base_url="http://x.x.x.x:9000/v1")

with user():
    llama2 += f'what is your name? '

with assistant():
    llama2 += gen("answer", stop='.')

print(llama2["answer"])
