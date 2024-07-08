from budserve import BudServe
from budserve.tasks import Summerization

client = BudServe(base_url="x.x.x.x:xxxx/v1", model_name="microsoft/Phi-3-mini-4k-instruct")


article = "You call transcription here"

summerizer = Summerization(client=client, num_sen=3, num_words=40)
summary = summerizer.summarize_text(text=article, topic="Support call transcription")
print(summary)