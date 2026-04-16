from langchain_core.prompts import PromptTemplate

scoring_prompt = PromptTemplate(
    input_variables=["match_result"],
    template="""
Assign score (0–100).

Rules:
- Start with 100
- Deduct 20 per missing skill
- Deduct 10 per missing year of experience

{match_result}

Return ONLY number.
"""
)