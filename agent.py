import json
from llm import ask_llm
from tools import search_web


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

def execute_action(action, job_description, candidate_profile):
    """
    Execute the action selected by the agent.
    """

    action_type = action.get("action")

    if action_type == "research_role":
        query = (
            f"requirements skills expectations for "
            f"{job_description[:500]}"
        )

        results = search_web(query, max_results=5)

        return {
            "action": "research_role",
            "query": query,
            "results": results
        }

    elif action_type == "analyze_candidate":
        return {
            "action": "analyze_candidate",
            "message": "Candidate profile analysis selected."
        }

    elif action_type == "evaluate_match":

        evaluation = evaluate_match(
            job_description,
            candidate_profile
        )

        return {
            "action": "evaluate_match",
            "evaluation": evaluation
        }

    elif action_type == "finish":
        return {
            "action": "finish",
            "message": "Agent decided that no additional action is required."
        }

    else:
        return {
            "action": "unknown",
            "message": f"Unknown action selected: {action_type}"
        }

def evaluate_match(job_description, candidate_profile):
    prompt = f"""
You are an evaluation component of an autonomous resume agent.

Evaluate how well the candidate matches the target job.

TARGET JOB DESCRIPTION:
{job_description}

CANDIDATE PROFILE:
{candidate_profile}

Analyze the match carefully.

Identify:
1. Strong matches
2. Weak or missing matches
3. Important evidence gaps
4. Overall match score from 0 to 100
5. Whether additional research or evidence gathering is needed

Return ONLY valid JSON in this format:

{{
    "match_score": 0,
    "strong_matches": [
        "example"
    ],
    "weak_matches": [
        "example"
    ],
    "evidence_gaps": [
        "example"
    ],
    "needs_more_information": true,
    "reason": "short explanation"
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