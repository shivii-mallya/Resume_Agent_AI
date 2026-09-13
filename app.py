import streamlit as st
from agent import create_initial_plan, execute_action,run_agent_loop

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

        with st.spinner("🤖 Agent is working..."):

            result = run_agent_loop(
                job_description,
                candidate_profile,
                max_iterations=5
            )

        if "error" in result:

            st.error(result["error"])

        else:

            st.subheader("🤖 Agent Activity")

            for item in result["trace"]:

                stage = item.get("stage")

                if stage == "initial_decision":

                    st.write("### 🎯 Initial Goal & Decision")

                    plan = item["data"]

                    st.write(f"**Goal:** {plan['goal']}")

                    st.write("**Next Action:**")
                    st.info(
                        f"{plan['next_action']['action']} — "
                        f"{plan['next_action']['reason']}"
                    )

                elif stage == "decision":

                    st.write(
                        f"### 🧠 Decision — Iteration "
                        f"{item['iteration']}"
                    )

                    action = item["action"]

                    st.info(
                        f"**Action:** {action.get('action')}\n\n"
                        f"**Reason:** {action.get('reason', '')}"
                    )

                elif stage == "action_result":

                    result_data = item["result"]

                    st.write(
                        f"### ⚙️ Action Result — Iteration "
                        f"{item['iteration']}"
                    )

                    if result_data["action"] == "research_role":

                        st.success(
                            f"🔎 Search completed: "
                            f"{result_data['query']}"
                        )

                        for i, source in enumerate(
                            result_data["results"],
                            start=1
                        ):
                            st.write(
                                f"**{i}. {source['title']}**"
                            )
                            st.write(
                                source["content"][:400]
                            )
                            st.write(
                                f"🔗 {source['url']}"
                            )

                    elif result_data["action"] == "evaluate_match":

                        evaluation = result_data.get(
                            "evaluation"
                        )

                        if evaluation and "error" not in evaluation:

                            st.metric(
                                "Match Score",
                                f"{evaluation['match_score']}%"
                            )

                            st.write("**Strong Matches**")

                            for item in evaluation[
                                "strong_matches"
                            ]:
                                st.write(f"✅ {item}")

                            st.write("**Weak Matches**")

                            for item in evaluation[
                                "weak_matches"
                            ]:
                                st.write(f"⚠️ {item}")

                            st.write("**Evidence Gaps**")

                            for item in evaluation[
                                "evidence_gaps"
                            ]:
                                st.write(f"🔎 {item}")

                elif stage == "evaluation":

                    evaluation = item["evaluation"]

                    if "error" not in evaluation:

                        st.write("### 📊 Agent Evaluation")

                        st.metric(
                            "Match Score",
                            f"{evaluation['match_score']}%"
                        )

                        if evaluation[
                            "needs_more_information"
                        ]:
                            st.warning(
                                "⚠️ Evidence is insufficient. "
                                "Agent will adapt."
                            )
                        else:
                            st.success(
                                "✅ Evidence appears sufficient."
                            )

                elif stage == "adaptation":

                    decision = item["decision"]

                    st.write(
                        f"### 🔄 Adaptation — Iteration "
                        f"{item['iteration']}"
                    )

                    st.info(
                        f"Agent decided to: "
                        f"**{decision.get('decision')}**\n\n"
                        f"Reason: {decision.get('reason')}"
                    )

                elif stage == "resume_generated":

                        resume = item["resume"]

                        if "error" in resume:

                            st.error(
                                "❌ Resume generation failed."
                            )

                            st.write(
                                resume["error"]
                            )

                            st.write("### Raw LLM Response")

                            st.code(
                                resume.get("raw_response", ""),
                                language="text"
                            )

                        else:

                            st.write("### 📄 Tailored Resume")

                            st.header(resume["name"])

                            st.write(
                                f"**{resume['headline']}**"
                            )

                            st.write("### Professional Summary")

                            st.write(
                                resume["summary"]
                            )

                            st.write("### Skills")

                            st.write(
                                ", ".join(resume["skills"])
                            )

                            st.write("### Projects")

                            for project in resume["projects"]:

                                st.write(
                                    f"**{project['name']}**"
                                )

                                st.write(
                                    project["description"]
                                )

                            st.write("### Experience")

                            for experience in resume["experience"]:

                                st.write(
                                    f"**{experience['title']} — "
                                    f"{experience['organization']}**"
                                )

                                st.write(
                                    experience["description"]
                                )

                            st.write("### Education")

                            for education in resume["education"]:

                                st.write(
                                    f"**{education['degree']} — "
                                    f"{education['institution']}**"
                                )

                                st.write(
                                    education["details"]
                                )

                            st.success(
                                "✅ Resume generated successfully."
                            )