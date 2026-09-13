import streamlit as st
from io import BytesIO
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas

from agent import create_initial_plan, execute_action, run_agent_loop

# -------------------------------------------------
# PDF generation — existing functionality preserved
# -------------------------------------------------
def create_resume_pdf(resume):
    """Create a simple PDF from the generated resume."""

    buffer = BytesIO()

    pdf = canvas.Canvas(buffer, pagesize=A4)

    width, height = A4
    y = height - 50

    def write_line(text, size=10, gap=16):
        nonlocal y

        if y < 50:
            pdf.showPage()
            y = height - 50

        pdf.setFont("Helvetica", size)

        words = str(text).split()
        line = ""

        for word in words:
            test_line = line + " " + word

            if pdf.stringWidth(test_line, "Helvetica", size) > width - 80:
                pdf.drawString(40, y, line)
                y -= gap
                line = word
            else:
                line = test_line

        if line:
            pdf.drawString(40, y, line)
            y -= gap

    write_line(resume["name"], 18, 24)
    write_line(resume["headline"], 11, 18)

    y -= 8

    write_line("PROFESSIONAL SUMMARY", 13, 20)
    write_line(resume["summary"], 10, 15)

    y -= 8

    write_line("SKILLS", 13, 20)
    write_line(", ".join(resume["skills"]), 10, 15)

    y -= 8

    write_line("PROJECTS", 13, 20)

    for project in resume["projects"]:
        write_line(project["name"], 11, 17)
        write_line(project["description"], 10, 15)

    y -= 8

    write_line("EXPERIENCE", 13, 20)

    for experience in resume["experience"]:
        write_line(
            f"{experience['title']} — "
            f"{experience['organization']}",
            11,
            17
        )
        write_line(experience["description"], 10, 15)

    y -= 8

    write_line("EDUCATION", 13, 20)

    for education in resume["education"]:
        write_line(
            f"{education['degree']} — "
            f"{education['institution']}",
            11,
            17
        )
        write_line(education["details"], 10, 15)

    pdf.save()

    buffer.seek(0)

    return buffer


# -------------------------------------------------
# Page setup + lightweight UI styling
# -------------------------------------------------
st.set_page_config(
    page_title="ResumeAgent AI",
    page_icon="🤖",
    layout="wide"
)

st.markdown(
    """
    <style>
        .main-title {
            font-size: 2.4rem;
            font-weight: 700;
            margin-bottom: 0.1rem;
        }

        .subtitle {
            color: #9fb3c8;
            font-size: 1rem;
            margin-bottom: 1.5rem;
        }

        .section-label {
            font-size: 1.05rem;
            font-weight: 650;
            margin-top: 0.6rem;
            margin-bottom: 0.4rem;
        }

        .status-card {
            padding: 1rem 1.2rem;
            border-radius: 12px;
            border: 1px solid rgba(100, 160, 220, 0.25);
            background: rgba(30, 65, 100, 0.25);
            margin: 0.8rem 0 1.2rem 0;
        }

        .resume-card {
            padding: 1.5rem;
            border-radius: 14px;
            border: 1px solid rgba(100, 160, 220, 0.30);
            background: rgba(25, 45, 70, 0.20);
        }

        div[data-testid="stExpander"] {
            border-radius: 10px;
            border: 1px solid rgba(100, 160, 220, 0.20);
        }

        .small-muted {
            color: #9fb3c8;
            font-size: 0.9rem;
        }
    </style>
    """,
    unsafe_allow_html=True
)

# -------------------------------------------------
# Header
# -------------------------------------------------
st.markdown(
    '<div class="main-title">🤖 ResumeAgent AI</div>',
    unsafe_allow_html=True
)
st.markdown(
    '<div class="subtitle">Autonomous AI agent for job research, candidate evaluation, and tailored resume generation.</div>',
    unsafe_allow_html=True
)

st.divider()

# -------------------------------------------------
# Inputs
# -------------------------------------------------
st.markdown('<div class="section-label">🎯 Target Job Description</div>', unsafe_allow_html=True)
job_description = st.text_area(
    "Paste the job description here",
    height=220,
    placeholder="Paste the complete job description...",
    label_visibility="collapsed"
)

st.markdown('<div class="section-label">👤 Candidate Profile</div>', unsafe_allow_html=True)
candidate_profile = st.text_area(
    "Paste your resume/profile here",
    height=220,
    placeholder="Paste your resume, projects, skills and experience...",
    label_visibility="collapsed"
)

st.write("")

if st.button("🚀 Start Application Agent", type="primary", use_container_width=True):

    if not job_description.strip():
        st.warning("Please enter a job description.")

    elif not candidate_profile.strip():
        st.warning("Please enter the candidate profile.")

    else:

        with st.spinner("🤖 Agent is working through the job analysis and resume generation..."):

            result = run_agent_loop(
                job_description,
                candidate_profile,
                max_iterations=5
            )

        if "error" in result:

            st.error(result["error"])

        else:

            # -------------------------------------------------
            # Agent status summary
            # -------------------------------------------------
            trace = result.get("trace", [])
            decisions = [
                item for item in trace
                if item.get("stage") == "decision"
            ]
            final_resume = None
            final_evaluation = None

            for item in trace:
                if item.get("stage") == "resume_generated":
                    final_resume = item.get("resume")
                elif item.get("stage") == "evaluation":
                    evaluation = item.get("evaluation")
                    if evaluation and "error" not in evaluation:
                        final_evaluation = evaluation

            st.markdown("### 🤖 Agent Activity")

            status_text = "Completed"
            status_color = "🟢"

            st.markdown(
                f"""
                <div class="status-card">
                    <strong>{status_color} Agent Status: {status_text}</strong><br>
                    <span class="small-muted">
                        {len(decisions)} decision step(s) recorded during the autonomous run.
                    </span>
                </div>
                """,
                unsafe_allow_html=True
            )

            # -------------------------------------------------
            # Compact trace — details remain available
            # -------------------------------------------------
            for item in trace:

                stage = item.get("stage")

                if stage == "initial_decision":

                    plan = item["data"]

                    with st.expander("🎯 Initial Goal & Decision", expanded=True):
                        st.write(f"**Goal:** {plan['goal']}")
                        st.write(
                            f"**Next Action:** {plan['next_action']['action']}"
                        )
                        st.caption(plan["next_action"].get("reason", ""))

                elif stage == "decision":

                    action = item["action"]

                    with st.expander(
                        f"🧠 Decision — Iteration {item['iteration']}: {action.get('action')}",
                        expanded=False
                    ):
                        st.write(f"**Action:** {action.get('action')}")
                        st.write(f"**Reason:** {action.get('reason', '')}")

                elif stage == "action_result":

                    result_data = item["result"]
                    action_name = result_data.get("action", "unknown")

                    # Resume results are shown in the final section below.
                    if action_name == "generate_resume":
                        continue

                    with st.expander(
                        f"⚙️ Action Result — Iteration {item['iteration']}: {action_name}",
                        expanded=False
                    ):

                        if action_name == "research_role":

                            st.success(
                                f"🔎 Search completed: {result_data.get('query', '')}"
                            )

                            for i, source in enumerate(
                                result_data.get("results", []),
                                start=1
                            ):
                                st.write(f"**{i}. {source['title']}**")
                                st.write(source["content"][:400])
                                st.write(f"🔗 {source['url']}")

                        elif action_name == "evaluate_match":

                            evaluation = result_data.get("evaluation")

                            if evaluation and "error" not in evaluation:

                                st.metric(
                                    "Match Score",
                                    f"{evaluation['match_score']}%"
                                )

                                st.write("**Strong Matches**")
                                for value in evaluation.get("strong_matches", []):
                                    st.write(f"✅ {value}")

                                st.write("**Weak Matches**")
                                for value in evaluation.get("weak_matches", []):
                                    st.write(f"⚠️ {value}")

                                st.write("**Evidence Gaps**")
                                for value in evaluation.get("evidence_gaps", []):
                                    st.write(f"🔎 {value}")

                        else:
                            st.write(result_data)

                elif stage == "evaluation":

                    evaluation = item["evaluation"]

                    if "error" not in evaluation:

                        with st.expander(
                            f"📊 Agent Evaluation — {evaluation['match_score']}% match",
                            expanded=False
                        ):
                            st.metric(
                                "Match Score",
                                f"{evaluation['match_score']}%"
                            )

                            if evaluation.get("needs_more_information"):
                                st.warning(
                                    "⚠️ Evidence is insufficient. Agent will adapt."
                                )
                            else:
                                st.success(
                                    "✅ Evidence appears sufficient."
                                )

                elif stage == "adaptation":

                    decision = item["decision"]

                    with st.expander(
                        f"🔄 Adaptation — Iteration {item['iteration']}: {decision.get('decision')}",
                        expanded=False
                    ):
                        st.write(
                            f"**Agent decided to:** {decision.get('decision')}"
                        )
                        st.write(f"**Reason:** {decision.get('reason', '')}")

                elif stage == "resume_generated":
                    # Render the final resume only once below.
                    continue

            # -------------------------------------------------
            # Final resume
            # -------------------------------------------------
            if final_resume:

                st.divider()
                st.markdown("## 📄 Final Tailored Resume")

                if "error" in final_resume:

                    st.error("❌ Resume generation failed.")
                    st.write(final_resume.get("error", "Unknown error"))

                    if final_resume.get("raw_response"):
                        with st.expander("View raw LLM response"):
                            st.code(
                                final_resume["raw_response"],
                                language="text"
                            )

                else:

                    st.markdown('<div class="resume-card">', unsafe_allow_html=True)

                    st.header(final_resume["name"])
                    st.write(f"**{final_resume['headline']}**")

                    st.subheader("Professional Summary")
                    st.write(final_resume["summary"])

                    st.subheader("Skills")
                    st.write(", ".join(final_resume["skills"]))

                    st.subheader("Projects")
                    for project in final_resume["projects"]:
                        st.write(f"**{project['name']}**")
                        st.write(project["description"])

                    st.subheader("Experience")
                    for experience in final_resume["experience"]:
                        st.write(
                            f"**{experience['title']} — "
                            f"{experience['organization']}**"
                        )
                        st.write(experience["description"])

                    st.subheader("Education")
                    for education in final_resume["education"]:
                        st.write(
                            f"**{education['degree']} — "
                            f"{education['institution']}**"
                        )
                        st.write(education["details"])

                    st.markdown('</div>', unsafe_allow_html=True)

                    st.success("✅ Resume generated successfully.")

                    pdf_file = create_resume_pdf(final_resume)

                    st.download_button(
                        label="⬇️ Download Resume as PDF",
                        data=pdf_file,
                        file_name="tailored_resume.pdf",
                        mime="application/pdf",
                        type="primary"
                    )

            elif final_evaluation:
                st.info(
                    "Agent completed its evaluation, but no final resume was returned."
                )
