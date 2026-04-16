from langchain_core.prompts import PromptTemplate

extraction_prompt = PromptTemplate(
    input_variables=["resume"],
    template="""
You are a resume analyzer.

Extract:
- Skills
- Experience
- Tools

Resume:
{resume}

Return ONLY valid JSON. No explanation.

{{
  "skills": [],
  "experience": "",
  "tools": []
}}
"""
)