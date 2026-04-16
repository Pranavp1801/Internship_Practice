from prompts.scoring_prompt import scoring_prompt
from utils.config import get_llm

llm = get_llm(temperature=0.0)

scoring_chain = scoring_prompt | llm