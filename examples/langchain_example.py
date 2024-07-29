from budserve.models.langchain import BudServeClient
from langchain_core.prompts import PromptTemplate
from langchain.schema.output_parser import StrOutputParser


llm = BudServeClient(base_url="http://x.x.x.x:9000/v1",
                 model_name="microsoft/Phi-3-medium-4k-instruct",
                 api_key="xxxxxxxxxxxxx")

prompt_template = PromptTemplate.from_template("Tell me a joke about {topic}")

chain = prompt_template | llm | StrOutputParser()

print(chain.invoke("cat"))