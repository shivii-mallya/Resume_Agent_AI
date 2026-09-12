import streamlit as st
from agent import create_initial_plan, execute_action

st.set_page_config(
    page_title="ResumeAgent AI",
    page_icon="🤖",
    layout="wide"
)

st.title("🤖 ResumeAgent AI")
st.write(
    "Autonomous Resume & Application Preparation Agent"
)

st.divider()

st.subheader("Target Job Description")

job_description = st.text_area(
    "Paste the job description here",
    height=250,
    placeholder="Paste the complete job description..."
)

st.subheader("Candidate Profile")

candidate_profile = st.text_area(
    "Paste your resume/profile here",
    height=250,
    placeholder="Paste your resume, projects, skills and experience..."
)

if st.button("🚀 Start Application Agent", type="primary"):

    if not job_description.strip():
        st.warning("Please enter a job description.")
    elif not candidate_profile.strip():
        st.warning("Please enter the candidate profile.")
    else:
        st.success("Inputs received. Agent is analyzing the application goal...")

        with st.spinner("🤖 Agent is analyzing the job and candidate..."):
            plan = create_initial_plan(
                job_description,
                candidate_profile
            )

        st.subheader("🧠 Agent's Initial Decision")

        if "error" in plan:
            st.error(plan["error"])
            st.code(plan["raw_response"])
        else:
            st.write("### 🎯 Goal")
            st.write(plan["goal"])

            st.write("### 📋 Job Requirements")
            for requirement in plan["job_requirements"]:
                st.write(f"- {requirement}")

            st.write("### 👤 Relevant Candidate Evidence")
            for evidence in plan["relevant_candidate_evidence"]:
                st.write(f"- {evidence}")

            st.write("### ⚠️ Information Gaps")
            for gap in plan["information_gaps"]:
                st.write(f"- {gap}")

            st.write("### 🔄 Next Action")

            action = plan["next_action"]

            st.info(
                f"**Action:** {action['action']}\n\n"
                f"**Reason:** {action['reason']}"
            )
            st.write("### ⚙️ Executing Action")

            with st.spinner("🔎 Agent is executing its selected action..."):
                action_result = execute_action(
                    action,
                    job_description,
                    candidate_profile
                )

            if action_result["action"] == "research_role":

                st.success(
                    f"Search completed: {action_result['query']}"
                )

                st.write("### 📚 Research Results")

                for i, result in enumerate(
                    action_result["results"], start=1
                ):
                    st.write(f"**{i}. {result['title']}**")
                    st.write(result["content"][:500])
                    st.write(f"🔗 {result['url']}")
                    st.divider()

            elif action_result["action"] == "evaluate_match":

                evaluation = action_result["evaluation"]

                if "error" in evaluation:
                    st.error(evaluation["error"])
                    st.code(evaluation["raw_response"])

                else:
                    st.write("### 📊 Match Evaluation")

                    st.metric(
                        "Overall Match",
                        f"{evaluation['match_score']}%"
                    )

                    st.write("#### ✅ Strong Matches")

                    for item in evaluation["strong_matches"]:
                        st.write(f"- {item}")

                    st.write("#### ⚠️ Weak Matches")

                    for item in evaluation["weak_matches"]:
                        st.write(f"- {item}")

                    st.write("#### 🔎 Evidence Gaps")

                    for item in evaluation["evidence_gaps"]:
                        st.write(f"- {item}")

                    if evaluation["needs_more_information"]:
                        st.warning(
                            f"🔄 More information is needed. "
                            f"{evaluation['reason']}"
                        )
                    else:
                        st.success(
                            f"✅ Evidence appears sufficient. "
                            f"{evaluation['reason']}"
                        )

            else:
                st.info(action_result["message"])