from ..utils import extract_yaml
from ..budserve import BudServe
COD_PROMPT = """
I will provide you with piece of content (e.g. articles, papers, documentation, etc.)

You will generate increasingly concise, entity-dense summaries of the content.

Repeat the following 2 steps 5 times.

Step 1. Identify 1-3 informative Entities (";" delimited) from the Article which are missing from the previously generated summary.

Step 2. Write a new, denser summary of identical length which covers every entity and detail from the previous summary plus the Missing Entities.

A Missing Entity is:

Relevant: to the main story.
Specific: descriptive yet concise (5 words or fewer).
Novel: not in the previous summary.
Faithful: present in the content piece.
Anywhere: located anywhere in the Article.

Guidelines:

The first summary should be long ({sc} sentences, -{wc} words) yet highly non-specific, containing little information beyond the entities marked as missing. Use overly verbose language and fillers (e.g., "this article discusses") to reach -{wc} words.
Make every word count: re-write the previous summary to improve flow and make space for additional entities.
Make space with fusion, compression, and removal of uninformative phrases like "the article discusses".
The summaries should become highly dense and concise yet self-contained, e.g., easily understood without the Article.
Missing entities can appear anywhere in the new summary.
Never drop entities from the previous summary. If space cannot be made, add fewer new entities.
Remember, use the exact same number of words for each summary.
Answer in JSON. The JSON should be a list (length 5) of dictionaries whose keys are "Missing_Entities" and "Denser_Summary".

Here is the input text for you to summarise using the 'Missing_Entities' and 'Denser_Summary' approach:

{text}
"""

SUMMARY_PROMPT = """
You are an expert in content summarization. Your task is to summarize the given content ({topic}) without losing any relevant information.

You will generate increasingly concise, entity-dense summaries of the content.

Guidelines:

The summary should be long ({sc} sentences, -{wc} words) yet highly specific.
The summaries should become highly dense and concise yet self-contained, e.g., easily understood without the content.
Remember, use the exact same number of words for the summary.

Here is the input text for you to summarise based on the given guidelines:

{text}

Answer should be in the following format.
```yaml
Denser_Summary: Give the summary as per the given guidelines
```
"""

class Summerization():
    '''
    client: BudServe client which connect with the server for inference
    num_sen: Required number of sentences for the summary. Default value: 4
    num_words: Total number of required words in the summary. Default value: 80
    '''
    def __init__(self, 
                 client: BudServe,
                 num_sen: int = 4,
                 num_words: int =  80) -> None:
        
        self.client = client
        self.num_sen = num_sen
        self.num_words = num_words
        
    def get_prompt(self, template, text, topic):
        if self.num_sen > 1:
            sc = f"{self.num_sen-1} - {self.num_sen}"
        prompt = template.format(text=text, sc=sc, wc=self.num_words, topic=topic)
        return prompt
    
    def summarize_text(self, text, topic="Article"):
        '''
        text: The content which needs to be summarised
        topic: The type of content which provided for summarisation. 
                This helps to align the model generation to specific domain.
                eg: Article, paper, documentation, call transcription etc
        '''

        prompt = self.get_prompt(SUMMARY_PROMPT, text, topic)

        completion = self.client.chat.completions.create(
            model=self.client.model_name,
            messages=[{"role": "user", "content": prompt}],
            max_tokens=800
        )

        try:
            summary = extract_yaml(completion.choices[0].message.content)
            sum_text = summary['Denser_Summary']
        except:
            sum_text = self.summarize_text(text=text)
        
        return sum_text

    def advanced_summarize_text(self, text, topic="Article"):

        prompt = self.get_prompt(COD_PROMPT, text, topic)

        completion = self.client.chat.completions.create(
            model=self.client.model_name,
            messages=[{"role": "user", "content": prompt}],
            max_tokens=800
        )

        return completion.choices[0].message.content