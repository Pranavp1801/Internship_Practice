from prompts.matching_prompt import matching_prompt
from utils.config import get_llm

llm = get_llm(temperature=0.2)

matching_chain = matching_prompt | llm