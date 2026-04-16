from prompts.explanation_prompt import explanation_prompt
from utils.config import get_llm

llm = get_llm(temperature=0.3)

explanation_chain = explanation_prompt | llm