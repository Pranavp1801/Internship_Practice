from prompts.extraction_prompt import extraction_prompt
from utils.config import get_llm

llm = get_llm(temperature=0.0)

extraction_chain = extraction_prompt | llm