from chains.extraction_chain import extraction_chain
from chains.matching_chain import matching_chain
from chains.scoring_chain import scoring_chain
from chains.explanation_chain import explanation_chain

# Job Description
job_description = """
Looking for Data Scientist with:
- Python
- Machine Learning
- SQL
- 2+ years experience
"""

# Test Resume
resume = """
I know Python and Pandas.
Worked on data analysis projects.
1 year experience.
"""

# Step 1: Extraction
extracted = extraction_chain.invoke({
    "resume": resume
}).content

# Step 2: Matching
match = matching_chain.invoke({
    "resume_data": extracted,
    "job_description": job_description
}).content

# Step 3: Scoring
score = scoring_chain.invoke({
    "match_result": match
}).content

# Step 4: Explanation
explanation = explanation_chain.invoke({
    "score": score,
    "match_result": match
}).content

# Output
print("\n=== Extracted Data ===")
print(extracted)

print("\n=== Matching ===")
print(match)

print("\n=== Score ===")
print(score)

print("\n=== Explanation ===")
print(explanation)