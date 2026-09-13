import streamlit as st
from io import BytesIO
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas

from agent import create_initial_plan, execute_action, run_agent_loop

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

        # Keep long text within the page
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

    # Name
    write_line(resume["name"], 18, 24)

    # Headline
    write_line(resume["headline"], 11, 18)

    y -= 8

    # Summary
    write_line("PROFESSIONAL SUMMARY", 13, 20)
    write_line(resume["summary"], 10, 15)

    y -= 8

    # Skills
    write_line("SKILLS", 13, 20)
    write_line(", ".join(resume["skills"]), 10, 15)

    y -= 8

    # Projects
    write_line("PROJECTS", 13, 20)

    for project in resume["projects"]:
        write_line(project["name"], 11, 17)
        write_line(project["description"], 10, 15)

    y -= 8

    # Experience
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

    # Education
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
                            pdf_file = create_resume_pdf(resume)

                            st.download_button(
                                label="⬇️ Download Resume as PDF",
                                data=pdf_file,
                                file_name="tailored_resume.pdf",
                                mime="application/pdf"
                            )