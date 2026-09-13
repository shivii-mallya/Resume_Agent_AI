# 🤖 ResumeAgent AI

An autonomous AI agent that researches job roles, evaluates candidate-job fit, adapts its research strategy, and generates a truthful, tailored resume.

Built for the Agentic AI Hackathon.

---

## 🎯 Problem

Creating a resume for every job application is time-consuming.

A candidate needs to:

- Understand what skills a job requires
- Research the role and industry expectations
- Compare their existing skills and projects with the role
- Identify important gaps
- Tailor their resume without exaggerating their experience

Most resume tools simply generate text from a prompt. They do not independently decide what information they need or what action to take next.

---

## 💡 Solution

ResumeAgent AI uses an autonomous agent workflow.

Instead of directly asking an LLM to write a resume, the agent:

1. Creates an initial plan
2. Decides what action should be performed
3. Researches the target role using web search
4. Evaluates the candidate's match with the role
5. Decides whether additional research is needed
6. Generates a truthful, job-tailored resume
7. Produces a downloadable PDF resume

The agent is designed to use only information provided about the candidate and does not invent experience or achievements.

---

## 🧠 Agentic Workflow

```text
                    ┌─────────────────────┐
                    │   Job Description   │
                    │ + Candidate Profile │
                    └──────────┬──────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │   Initial Planner   │
                    │  Decide next action │
                    └──────────┬──────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │    Action Agent     │
                    └──────────┬──────────┘
                               │
              ┌────────────────┼────────────────┐
              ▼                ▼                ▼
        ┌───────────┐   ┌──────────────┐  ┌──────────────┐
        │ Research  │   │ Match        │  │ Generate     │
        │ Job Role  │   │ Evaluation   │  │ Resume       │
        └─────┬─────┘   └──────┬───────┘  └──────┬───────┘
              │                │                  │
              └────────────────┼──────────────────┘
                               ▼
                    ┌─────────────────────┐
                    │  Evaluate Result    │
                    └──────────┬──────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │ Decide Next Action  │
                    │    / Adapt Strategy │
                    └──────────┬──────────┘
                               │
                    ┌──────────┴──────────┐
                    │                     │
              More research?          Enough?
                    │                     │
                    ▼                     ▼
                Continue            Generate Resume
                                          │
                                          ▼
                                 ┌─────────────────┐
                                 │ Downloadable PDF│
                                 └─────────────────┘

```

✨ Features
Autonomous Decision Making

The agent decides which action to perform instead of following a completely fixed sequence.

🔎 Job Role Research

Uses Tavily to search the web for relevant information about the target role.

📊 Candidate-Job Matching

Compares the job requirements with the candidate's existing skills, projects, and experience.

🔄 Adaptive Research

The agent can use the results of previous actions to decide what information should be investigated next.

📄 Truthful Resume Generation

The generated resume is based only on the candidate information provided.

The system is explicitly instructed not to invent:

Experience
Companies
Projects
Skills
Degrees
Dates
Achievements
⬇️ PDF Resume Download

The final tailored resume can be downloaded directly as a PDF from the Streamlit interface.

🛠️ Tech Stack
Technology	Purpose
Python	Core application and agent logic
Streamlit	Web interface
Groq	LLM inference
Tavily	Web research
ReportLab	PDF resume generation
python-dotenv	Environment variable management

📁 Project Structure
Resume_Agent_AI/
│
├── app.py              # Streamlit user interface
├── agent.py            # Autonomous agent logic
├── llm.py              # Groq LLM integration
├── tools.py            # External tools such as web research
├── prompts.py          # Prompt definitions
├── requirements.txt    # Python dependencies
├── .gitignore          # Files excluded from Git
├── .env                # API keys (not committed)
└── venv/               # Local Python virtual environment

⚙️ How It Works
1. User Input
The user provides:
A target job description
Their candidate profile

2. Initial Planning
The agent analyzes the inputs and decides what action should be performed first.

3. Research
When appropriate, the agent searches the web using Tavily.
The research results provide additional context about the target role.

4. Evaluation
The agent evaluates how well the candidate matches the job requirements.

5. Adaptation
Based on the latest results, the agent decides whether it should:
Research further
Evaluate the candidate
Generate the resume
Finish

6. Resume Generation
Once enough information has been gathered, the agent generates a tailored resume.

7. PDF Output
The generated resume is formatted into a PDF that the user can download.


🚀 Setup
1. Clone the repository
git clone https://github.com/shivii-mallya/Resume_Agent_AI.git
cd Resume_Agent_AI

2. Create a virtual environment
python -m venv venv

3. Activate the virtual environment
Windows:
venv\Scripts\activate

4. Install dependencies
pip install -r requirements.txt

5. Configure API keys
Create a .env file in the project root:
GROQ_API_KEY=your_groq_api_key
TAVILY_API_KEY=your_tavily_api_key
Do not commit .env to GitHub.

6. Run the application
streamlit run app.py
The application will open in your browser.


🔐 Responsible Resume Generation
ResumeAgent AI is designed to preserve the accuracy of candidate information.
The LLM is instructed to use only truthful evidence supplied in the candidate profile.
This helps reduce the risk of AI-generated resumes containing fabricated experience or qualifications.


🔮 Future Improvements
Possible future enhancements include:
Resume quality self-evaluation
Automatic resume revision
Multiple resume templates
Job application tracking
Support for multiple job postings
Skill-gap learning recommendations
Export to DOCX
Improved PDF styling
Persistent candidate profiles

👩‍💻 Built With
Python • Streamlit • Groq • Tavily • ReportLab