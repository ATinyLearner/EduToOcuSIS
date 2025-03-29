import streamlit as st
import firebase_admin
from firebase_admin import credentials, firestore
import datetime
import pandas as pd
import time

# Load Firebase credentials from Streamlit secrets
firebase_secrets = st.secrets["firebase"]

# Initialize Firebase if not already initialized
if not firebase_admin._apps:
    cred = credentials.Certificate({
        "type": firebase_secrets["type"],
        "project_id": firebase_secrets["project_id"],
        "private_key_id": firebase_secrets["private_key_id"],
        "private_key": firebase_secrets["private_key"].replace("\\n", "\n"),
        "client_email": firebase_secrets["client_email"],
        "client_id": firebase_secrets["client_id"],
        "auth_uri": firebase_secrets["auth_uri"],
        "token_uri": firebase_secrets["token_uri"],
        "auth_provider_x509_cert_url": firebase_secrets["auth_provider_x509_cert_url"],
        "client_x509_cert_url": firebase_secrets["client_x509_cert_url"],
    })
    firebase_admin.initialize_app(cred)

# Get Firestore client
db = firestore.client()

# ---------- Sidebar Setup ----------
with st.sidebar:
    st.image("logo.png", use_container_width=True)
    st.header("Survey Progress")
    # Placeholders for progress bar and answered counter
    progress_bar = st.progress(0)
    answered_text = st.empty()

# ---------- Survey Data ----------
survey = {
    "Skills & Aptitude": [
        {
            "question": "When working on a project, you enjoy:",
            "options": {
                "A": "Solving complex problems through logic.",
                "B": "Generating creative and innovative ideas.",
                "C": "Collaborating with others.",
                "D": "Organizing and managing the project."
            }
        },
        {
            "question": "What are you naturally good at?",
            "options": {
                "A": "Analyzing data and drawing conclusions.",
                "B": "Designing or creating visual content.",
                "C": "Leading and mentoring.",
                "D": "Planning and streamlining processes."
            }
        },
        {
            "question": "What activity excites you the most?",
            "options": {
                "A": "Solving puzzles or logic problems.",
                "B": "Writing or creating visual designs.",
                "C": "Public speaking or debating.",
                "D": "Managing and organizing events."
            }
        },
        {
            "question": "How do you prefer to learn?",
            "options": {
                "A": "Through problem-solving.",
                "B": "Through creative, hands-on activities.",
                "C": "Through group discussions.",
                "D": "Through structured lessons."
            }
        },
        {
            "question": "What type of extracurricular activity appeals to you?",
            "options": {
                "A": "Math or science clubs.",
                "B": "Art or creative workshops.",
                "C": "Debate or public speaking.",
                "D": "Leadership activities."
            }
        },
        {
            "question": "When given a challenge, you:",
            "options": {
                "A": "Use data and logic to solve it.",
                "B": "Think creatively for new ideas.",
                "C": "Seek input from others.",
                "D": "Organize it into manageable steps."
            }
        },
        {
            "question": "Your preferred subject is:",
            "options": {
                "A": "Mathematics or Science.",
                "B": "Arts or Design.",
                "C": "Social Sciences.",
                "D": "Business or Economics."
            }
        },
        {
            "question": "What kind of work environment suits you?",
            "options": {
                "A": "Research-driven and analytical.",
                "B": "Creative and free-thinking.",
                "C": "Social and collaborative.",
                "D": "Structured and goal-oriented."
            }
        },
        {
            "question": "When solving a problem, you:",
            "options": {
                "A": "Follow logical, step-by-step reasoning.",
                "B": "Use creative and unconventional methods.",
                "C": "Collaborate with others for insights.",
                "D": "Plan and organize before acting."
            }
        },
        {
            "question": "What motivates you most?",
            "options": {
                "A": "Mastering complex skills.",
                "B": "Expressing creativity.",
                "C": "Making a social impact.",
                "D": "Achieving milestones and goals."
            }
        }
    ],
    "IQ & Analytical Thinking": [
        {
            "question": "If 5x + 10 = 35, what is x?",
            "options": {
                "A": "4",
                "B": "5",
                "C": "6",
                "D": "7"
            }
        },
        {
            "question": "Which number comes next: 2, 6, 12, 20, 30, ___?",
            "options": {
                "A": "42",
                "B": "45",
                "C": "52",
                "D": "60"
            }
        },
        {
            "question": "Which shape comes next in the sequence? (Insert visual)",
            "options": {
                "A": "Square",
                "B": "Triangle",
                "C": "Circle",
                "D": "Pentagon"
            }
        },
        {
            "question": "You are given a set of numbers: 12, 24, 36. What is the next number?",
            "options": {
                "A": "48",
                "B": "50",
                "C": "60",
                "D": "72"
            }
        },
        {
            "question": "You are asked to arrange items in alphabetical order. You:",
            "options": {
                "A": "Quickly follow the alphabet sequence.",
                "B": "Create your own coding system.",
                "C": "Collaborate with others for faster sorting.",
                "D": "Systematically categorize them first."
            }
        },
        {
            "question": "You find yourself in an escape room. What is your approach?",
            "options": {
                "A": "Use logic to solve the clues.",
                "B": "Think creatively to identify patterns.",
                "C": "Communicate with the team.",
                "D": "Organize the clues systematically."
            }
        },
        {
            "question": "You encounter a new problem. Your first instinct is to:",
            "options": {
                "A": "Analyze the data.",
                "B": "Think outside the box.",
                "C": "Ask for opinions.",
                "D": "Create a detailed plan."
            }
        },
        {
            "question": "When analyzing trends, you:",
            "options": {
                "A": "Identify patterns using data.",
                "B": "Create a visual representation.",
                "C": "Discuss with others for insights.",
                "D": "Create a timeline or structure."
            }
        },
        {
            "question": "When studying, you prefer:",
            "options": {
                "A": "Logical problem-solving exercises.",
                "B": "Drawing or creative activities.",
                "C": "Interactive group discussions.",
                "D": "Step-by-step guides."
            }
        },
        {
            "question": "Which of the following is the odd one out?",
            "options": {
                "A": "Cat",
                "B": "Dog",
                "C": "Carrot",
                "D": "Rabbit"
            }
        }
    ],
    "EQ & Emotional Intelligence": [
        {
            "question": "When dealing with criticism, you:",
            "options": {
                "A": "Learn from it.",
                "B": "Use it to improve creatively.",
                "C": "Discuss it with others.",
                "D": "Reflect before responding."
            }
        },
        {
            "question": "In stressful situations, you:",
            "options": {
                "A": "Stay calm and find solutions.",
                "B": "Express your emotions freely.",
                "C": "Talk it out with others.",
                "D": "Prioritize tasks."
            }
        },
        {
            "question": "How do you handle conflicts?",
            "options": {
                "A": "Use logic to find solutions.",
                "B": "Be creative and empathetic.",
                "C": "Collaborate for resolution.",
                "D": "Stick to structured discussions."
            }
        },
        {
            "question": "When making decisions, you:",
            "options": {
                "A": "Use logic and reasoning.",
                "B": "Trust your instincts.",
                "C": "Consider others’ opinions.",
                "D": "Follow structured analysis."
            }
        },
        {
            "question": "How do you recharge after a long day?",
            "options": {
                "A": "Solve puzzles or play strategic games.",
                "B": "Engage in creative activities.",
                "C": "Socialize with friends.",
                "D": "Organize your space."
            }
        },
        {
            "question": "When helping others, you:",
            "options": {
                "A": "Offer practical solutions.",
                "B": "Use empathy and compassion.",
                "C": "Collaborate with them.",
                "D": "Create a structured plan."
            }
        },
        {
            "question": "When faced with emotional decisions, you:",
            "options": {
                "A": "Stay objective and logical.",
                "B": "Trust your gut feelings.",
                "C": "Rely on personal experiences.",
                "D": "Seek organized guidance."
            }
        },
        {
            "question": "When giving feedback, you:",
            "options": {
                "A": "Stay factual and logical.",
                "B": "Use creativity and kindness.",
                "C": "Be compassionate.",
                "D": "Keep it structured and clear."
            }
        },
        {
            "question": "When under pressure, you:",
            "options": {
                "A": "Focus on facts.",
                "B": "Stay flexible and creative.",
                "C": "Rely on others.",
                "D": "Follow a strict plan."
            }
        },
        {
            "question": "Your ideal workplace involves:",
            "options": {
                "A": "Logic and problem-solving.",
                "B": "Creativity and flexibility.",
                "C": "Collaboration.",
                "D": "Structured processes."
            }
        }
    ],
    "Cognitive Abilities & Learning Styles": [
        {
            "question": "When learning a new concept, you:",
            "options": {
                "A": "Analyze its details thoroughly.",
                "B": "Visualize it creatively.",
                "C": "Discuss it with peers.",
                "D": "Create a study plan."
            }
        },
        {
            "question": "You prefer tasks that involve:",
            "options": {
                "A": "Logical reasoning.",
                "B": "Imagination and creativity.",
                "C": "Collaboration and communication.",
                "D": "Structured organization."
            }
        },
        {
            "question": "You understand new topics better by:",
            "options": {
                "A": "Problem-solving exercises.",
                "B": "Drawing diagrams.",
                "C": "Group discussions.",
                "D": "Following step-by-step instructions."
            }
        },
        {
            "question": "You excel in:",
            "options": {
                "A": "Analytical thinking.",
                "B": "Artistic expression.",
                "C": "Verbal communication.",
                "D": "Systematic planning."
            }
        },
        {
            "question": "Your ideal project involves:",
            "options": {
                "A": "Data analysis.",
                "B": "Creative storytelling.",
                "C": "Team collaboration.",
                "D": "Planning and organization."
            }
        },
        {
            "question": "You process information best by:",
            "options": {
                "A": "Applying logic and reasoning.",
                "B": "Visualizing concepts.",
                "C": "Verbalizing and discussing.",
                "D": "Structuring it into steps."
            }
        },
        {
            "question": "Your preferred problem-solving strategy:",
            "options": {
                "A": "Break down problems systematically.",
                "B": "Use creative and abstract thinking.",
                "C": "Collaborate with others for solutions.",
                "D": "Follow a clear, structured process."
            }
        },
        {
            "question": "When faced with a challenge, you:",
            "options": {
                "A": "Rely on analysis and data.",
                "B": "Think imaginatively.",
                "C": "Consult with peers.",
                "D": "Create a step-by-step action plan."
            }
        },
        {
            "question": "Your ideal study method involves:",
            "options": {
                "A": "Solving logical problems.",
                "B": "Drawing or creative expression.",
                "C": "Group discussions and peer feedback.",
                "D": "Detailed, structured planning."
            }
        },
        {
            "question": "You learn best through:",
            "options": {
                "A": "Data-driven analysis.",
                "B": "Visual aids and illustrations.",
                "C": "Verbal communication.",
                "D": "Organized practice and repetition."
            }
        }
    ]
}

# ---------- Scoring Function ----------
def get_score(option):
    scores = {"A": 4, "B": 3, "C": 2, "D": 1}
    return scores.get(option, 0)

# ---------- Compute and Update Progress ----------
def compute_progress():
    total_questions = sum(len(questions) for questions in survey.values())
    answered = sum(
        1
        for section, questions in survey.items()
        for idx in range(1, len(questions) + 1)
        if st.session_state.get(f"radio_{section}_{idx}", "") != ""
    )
    progress = int((answered / total_questions) * 100)
    return answered, total_questions, progress

# ---------- Main App UI ----------
st.markdown("<h2 style='text-align: left; font-weight: bold;'>Skill Stork International School Presents</h2>", unsafe_allow_html=True)
st.title("Career Pathway Assessment Survey")
st.write("Click 'Start Survey' twice to begin.")

# ---------- Welcome Screen ----------
if not st.session_state.get("survey_started", False):
    if st.button("Start Survey"):
        st.session_state.survey_started = True
    st.stop()

# ---------- User Details ----------
st.header("Your Details")
full_name = st.text_input("Full Name", max_chars=100)
email = st.text_input("Email")
phone = st.text_input("Phone")
st.write("---")

# ---------- Survey Questions ----------
responses = {}
for section, questions in survey.items():
    st.header(section)
    for idx, item in enumerate(questions, start=1):
        qid = f"radio_{section}_{idx}"
        st.subheader(f"Q{idx}: {item['question']}")
        # Include empty option as default; its label will appear blank.
        options = [""] + list(item['options'].keys())
        choice = st.radio(
            "Select an option:",
            options,
            key=qid,
            format_func=lambda x: "" if x == "" else item['options'][x]
        )
        responses[qid] = choice

# ---------- Update Sidebar Progress After Rendering ----------
answered, total_questions, progress = compute_progress()
progress_bar.progress(progress)
answered_text.text(f"Answered: {answered}/{total_questions}")

# ---------- Submit Button ----------
if st.button("Submit Survey"):
    for percent_complete in range(0, 101, 5):
        time.sleep(0.03)
        progress_bar.progress(percent_complete)
    
    # ---------- Calculate Scores ----------
    section_scores = {
        "Skills & Aptitude": 0,
        "IQ & Analytical Thinking": 0,
        "EQ & Emotional Intelligence": 0,
        "Cognitive Abilities & Learning Styles": 0
    }
    for section in section_scores.keys():
        for idx in range(1, len(survey[section]) + 1):
            qid = f"radio_{section}_{idx}"
            answer = st.session_state.get(qid, "")
            section_scores[section] += get_score(answer)
    
    total_score = sum(section_scores.values())
    
    recommendations = []
    if section_scores["Skills & Aptitude"] >= 35 and section_scores["IQ & Analytical Thinking"] >= 35:
        recommendations.append("STEM Careers: Engineer, Data Scientist/Analyst, AI & Machine Learning Specialist, Software Developer")
    if section_scores["Skills & Aptitude"] >= 35 and section_scores["Cognitive Abilities & Learning Styles"] >= 50 and section_scores["EQ & Emotional Intelligence"] >= 35:
        recommendations.append("Business & Management: Entrepreneur/Business Owner, Marketing/Sales Manager, Financial Analyst, Management Consultant")
    if section_scores["Skills & Aptitude"] >= 35 and section_scores["Cognitive Abilities & Learning Styles"] >= 50 and section_scores["EQ & Emotional Intelligence"] < 35:
        recommendations.append("Creative Fields / Healthcare & Medicine: Consider roles such as Graphic Designer, UX/UI Designer, Content Creator, Media Production for creative fields; or Doctor, Biotechnologist, Geneticist, Healthcare Administrator for healthcare.")
    if section_scores["EQ & Emotional Intelligence"] >= 35 and section_scores["Cognitive Abilities & Learning Styles"] >= 50 and section_scores["Skills & Aptitude"] < 35:
        recommendations.append("Humanities & Social Sciences: Lawyer/Legal Consultant, Psychologist/Counselor, Journalist/Media Analyst, Human Resource Manager")
    
    # Additional recommendations based on overall total score
    if total_score < 60:
        recommendations.append("Entry-Level Roles: Administrative Assistant, Customer Service Representative, Sales Associate")
    elif total_score < 120:
        recommendations.append("Operations & Coordination: Project Coordinator, Office Manager, Supply Chain Analyst")
    else:
        recommendations.append("Leadership & Strategy: Business Strategist, Management Consultant, Operations Manager")
    
    data = {
        "timestamp": datetime.datetime.utcnow(),
        "full_name": full_name,
        "email": email,
        "phone": phone,
        "responses": {qid: st.session_state.get(qid, "") for section in survey for qid in [f"radio_{section}_{i}" for i in range(1, len(survey[section]) + 1)]},
        "section_scores": section_scores,
        "total_score": total_score,
        "recommendations": recommendations
    }
    
    try:
        db.collection("surveys").add(data)
        st.success("Your responses have been recorded successfully!")
    except Exception as e:
        st.error(f"An error occurred while saving your data: {e}")
    
    st.header("Your Assessment Report")
    st.subheader("Section-wise Scores")
    score_df = pd.DataFrame.from_dict(section_scores, orient='index', columns=['Score'])
    st.table(score_df)
    st.write(f"**Total Score:** {total_score} out of 180")
    # st.subheader("Career Pathway Recommendations")
    # if recommendations:
    #     for rec in recommendations:
    #         st.write(f"- {rec}")
    # else:
    #     st.write("No specific dominant pathway was identified. Consider exploring multiple fields based on your interests!")
    # st.subheader("Visual Score Representation")
    # st.bar_chart(score_df)
