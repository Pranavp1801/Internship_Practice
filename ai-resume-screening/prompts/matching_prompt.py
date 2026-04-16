from langchain_core.prompts import PromptTemplate

matching_prompt = PromptTemplate(
    input_variables=["resume_data", "job_description"],
    template="""
Compare resume with job description.

Resume:
{resume_data}

Job Description:
{job_description}

Return:
Matching Skills: ...
Missing Skills: ...
Missing Experience: ...

Keep answer short.
"""
)