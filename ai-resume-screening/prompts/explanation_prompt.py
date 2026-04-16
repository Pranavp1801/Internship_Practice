from langchain_core.prompts import PromptTemplate

explanation_prompt = PromptTemplate(
    input_variables=["score", "match_result"],
    template="""
Explain the score.

Score: {score}

{match_result}

Keep it short and clear.
"""
)