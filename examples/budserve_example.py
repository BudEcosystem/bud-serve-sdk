from budserve import BudServe

client = BudServe(base_url="http://x.x.x.x:xxxx/v1")

stream = client.chat.completions.create(
    model="meta-llama/Llama-2-7b-chat-hf",
    messages=[{"role": "user", "content": "write an essay about history of cricket"}],
    stream=True,
    max_tokens=200
)

for chunk in stream:
    print(chunk.choices[0].delta.content or "", end="", flush=True)
