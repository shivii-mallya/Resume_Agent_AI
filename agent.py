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

        query = action.get("search_query")

        if not query:
            query = (
                "software engineering internship skills "
                "requirements and expectations"
            )

        results = search_web(
            query,
            max_results=5
        )

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
def decide_next_action(
    job_description,
    candidate_profile,
    previous_actions,
    latest_result
):
    """
    Decide what the agent should do next based on
    the current state and the latest result.
    """

    prompt = f"""
You are the decision-making component of an autonomous
resume and job application agent.

Your ultimate goal is:

Prepare the strongest truthful application possible for
the target job using only evidence that can be supported.

TARGET JOB DESCRIPTION:
{job_description}

CANDIDATE PROFILE:
{candidate_profile}

ACTIONS ALREADY TAKEN:
{previous_actions}

LATEST RESULT:
{latest_result}

Available actions:

1. research_role
   Use web search when more information about the role,
   company, industry expectations, or relevant skills is needed.

2. evaluate_match
   Compare the candidate's evidence against the job requirements.

3. generate_resume
   Generate a tailored resume when there is enough information.

4. finish
   Finish when the available evidence is sufficient and
   the application is ready for the next stage.

IMPORTANT:
- Do not invent candidate experience.
- Do not claim the candidate has a skill unless supported
  by the candidate profile or verified evidence.
- If important information is missing, choose an action
  that can help resolve the gap.
- Do not repeatedly perform the same action without a reason.
- Make the decision based on the latest result.

Return ONLY valid JSON:

{{
    "decision": "research_role",
    "reason": "why this action is the best next step",
    "search_query": "search query if research_role is selected, otherwise empty"
}}

The decision MUST be exactly one of:

research_role
evaluate_match
generate_resume
finish
"""

    response = ask_llm(prompt)

    try:
        return json.loads(response)

    except json.JSONDecodeError:
        return {
            "error": "The LLM did not return valid JSON.",
            "raw_response": response
        }

def run_agent_loop(
    job_description,
    candidate_profile,
    max_iterations=3
):
    """
    Run the autonomous decision/action/evaluation loop.
    """

    trace = []

    # ---------------------------------------
    # STEP 1: Initial planning
    # ---------------------------------------

    plan = create_initial_plan(
        job_description,
        candidate_profile
    )

    if "error" in plan:
        return {
            "error": plan["error"],
            "trace": trace
        }

    current_action = plan["next_action"]

    trace.append({
        "stage": "initial_decision",
        "data": plan
    })

    previous_actions = []

    # ---------------------------------------
    # STEP 2: Autonomous loop
    # ---------------------------------------

    for iteration in range(max_iterations):

        action_type = current_action.get("action")

        previous_actions.append(action_type)

        trace.append({
            "stage": "decision",
            "iteration": iteration + 1,
            "action": current_action
        })

        # Execute the selected action
        action_result = execute_action(
            current_action,
            job_description,
            candidate_profile
        )

        trace.append({
            "stage": "action_result",
            "iteration": iteration + 1,
            "result": action_result
        })

        # ---------------------------------------
        # Evaluate match when selected
        # ---------------------------------------

        if action_type == "evaluate_match":

            evaluation = evaluate_match(
                job_description,
                candidate_profile
            )

            action_result["evaluation"] = evaluation

            trace.append({
                "stage": "evaluation",
                "iteration": iteration + 1,
                "evaluation": evaluation
            })

            latest_result = evaluation

        else:

            latest_result = action_result

        # ---------------------------------------
        # Stop if agent chooses to finish
        # ---------------------------------------

        if action_type == "finish":

            trace.append({
                "stage": "finished",
                "iteration": iteration + 1
            })

            break

        # ---------------------------------------
        # Ask agent what to do next
        # ---------------------------------------

        next_decision = decide_next_action(
            job_description,
            candidate_profile,
            previous_actions,
            latest_result
        )

        trace.append({
            "stage": "adaptation",
            "iteration": iteration + 1,
            "decision": next_decision
        })

        if "error" in next_decision:
            break

        current_action = {
            "action": next_decision["decision"],
            "reason": next_decision["reason"],
            "search_query": next_decision.get(
                "search_query",
                ""
            )
        }

    return {
        "plan": plan,
        "trace": trace
    }

if __name__ == "__main__":

    test_job = """
    Software Engineering Intern.

    Requirements:
    Python, REST APIs, SQL, Git, problem solving,
    software development projects.
    """

    test_candidate = """
    Second-year Computer Science student.

    Skills:
    Python, C++, SQL, Git, GitHub, Streamlit.

    Projects:
    Built a voice-based task management application
    using Python, Streamlit, SQLite and an LLM API.

    Built an ESP32 gas monitoring system with a Python dashboard.
    """

    result = run_agent_loop(
        test_job,
        test_candidate
    )

    for item in result["trace"]:
        print("\n" + "=" * 60)
        print(item)