import json
from llm import ask_llm


def create_initial_plan(job_description, candidate_profile):
    prompt = f"""
You are the planning agent for an autonomous resume and job application
preparation system.

Your goal is to help prepare a strong, truthful, role-specific application.

You have two inputs.

TARGET JOB DESCRIPTION:
{job_description}

CANDIDATE PROFILE:
{candidate_profile}

Analyze the job description and candidate profile.

Determine:

1. The important requirements of the job.
2. Which candidate skills/projects/experience are relevant.
3. What information is missing or needs verification.
4. What actions the agent should take next.

Possible actions are:
- "research_role"
- "analyze_candidate"
- "evaluate_match"
- "finish"

Return ONLY valid JSON in this exact structure:

{{
    "goal": "short description of the application goal",
    "job_requirements": [
        "requirement 1",
        "requirement 2"
    ],
    "relevant_candidate_evidence": [
        "evidence 1",
        "evidence 2"
    ],
    "information_gaps": [
        "gap 1",
        "gap 2"
    ],
    "next_action": {{
        "action": "research_role",
        "reason": "why this action is needed"
    }}
}}
"""

    response = ask_llm(prompt)

    try:
        return json.loads(response)
    except json.JSONDecodeError:
        return {
            "error": "The LLM did not return valid JSON.",
            "raw_response": response
        }