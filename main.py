from fastapi import FastAPI, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
import PyPDF2
import docx
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import spacy

from database import engine, SessionLocal
from models import Base, Skill, Training
from role_classifier import classify_role

# ---------------- INIT ----------------

nlp = spacy.load("en_core_web_sm")

Base.metadata.create_all(bind=engine)

app = FastAPI(title="SkillGapAI AI Engine")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------------- ROOT ----------------

@app.get("/")
def home():
    return {
        "project": "SkillGapAI",
        "status": "AI Engine Running 🚀",
        "docs": "/docs"
    }

# ---------------- STARTUP SEED ----------------

@app.on_event("startup")
def startup_event():
    db = SessionLocal()

    if not db.query(Skill).first():
        print("Seeding database...")

        skills_data = [
            ("python", "Programming"),
            ("java", "Programming"),
            ("machine learning", "AI/ML"),
            ("deep learning", "AI/ML"),
            ("tensorflow", "AI/ML"),
            ("aws", "Cloud"),
            ("docker", "DevOps"),
            ("react", "Web Development"),
        ]

        for name, category in skills_data:
            db.add(Skill(name=name, category=category))

        training_data = [
            ("python", "Python Mastery", "Udemy", "Beginner"),
            ("machine learning", "ML Specialization", "Coursera", "Intermediate"),
            ("docker", "Docker Essentials", "Udemy", "Intermediate"),
        ]

        for skill_name, course, provider, level in training_data:
            db.add(Training(
                skill_name=skill_name,
                course_name=course,
                provider=provider,
                level=level
            ))

        db.commit()

    db.close()
    print("🚀 SkillGapAI Running")
    print("👉 http://127.0.0.1:8000/docs\n")

# ---------------- TEXT EXTRACTION ----------------

def extract_text(file: UploadFile):
    text = ""

    if file.filename.endswith(".pdf"):
        pdf_reader = PyPDF2.PdfReader(file.file)
        for page in pdf_reader.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text

    elif file.filename.endswith(".docx"):
        doc = docx.Document(file.file)
        for para in doc.paragraphs:
            text += para.text + " "

    else:
        text = file.file.read().decode("utf-8")

    return text.lower()

# ---------------- MAIN AI ROUTE ----------------

@app.post("/analyze-role")
async def analyze_role(
    resume: UploadFile = File(...),
    role: str = Form(...)
):
    db = SessionLocal()

    resume_text = extract_text(resume)
    role_text = role.lower()

    # -------- 1️⃣ Role Classification --------
    predicted_role = classify_role(resume_text)

    # -------- 2️⃣ Semantic Similarity --------
    vectorizer = TfidfVectorizer(stop_words="english")
    tfidf_matrix = vectorizer.fit_transform([resume_text, role_text])

    similarity_score = cosine_similarity(
        tfidf_matrix[0:1],
        tfidf_matrix[1:2]
    )[0][0]

    semantic_score = int(similarity_score * 100)

    # -------- 3️⃣ Skill Matching --------
    all_skills = db.query(Skill).all()

    matched_skills = []
    missing_skills = []

    for skill in all_skills:
        skill_name = skill.name.lower()
        if skill_name in resume_text:
            matched_skills.append(skill_name)
        else:
            missing_skills.append(skill_name)

    skill_match_score = int(
        (len(matched_skills) / len(all_skills)) * 100
    ) if all_skills else 0

    # -------- 4️⃣ Final Combined Score --------
    overall_match = int(
        (semantic_score * 0.5) + (skill_match_score * 0.5)
    )

    # -------- 5️⃣ Category Breakdown --------
    category_scores = {}
    categories = {}

    for skill in all_skills:
        categories.setdefault(skill.category, []).append(skill.name.lower())

    for category, skills in categories.items():
        role_skills = [s for s in skills if s in role_text]

        if not role_skills:
            continue

        resume_skills = [s for s in role_skills if s in resume_text]

        score = int((len(resume_skills) / len(role_skills)) * 100)
        category_scores[category] = score

    # -------- 6️⃣ Training Recommendations --------
    recommendations = []

    for skill in missing_skills[:5]:
        training = db.query(Training).filter(
            Training.skill_name == skill
        ).first()

        if training:
            recommendations.append({
                "skill": skill,
                "course": training.course_name,
                "provider": training.provider,
                "level": training.level
            })

    db.close()

    return {
        "predicted_role": predicted_role,
        "overall_match_percentage": overall_match,
        "category_breakdown": category_scores,
        "matched_skills": matched_skills,
        "missing_skills": missing_skills,
        "recommendations": recommendations,
        "analysis_summary":
            f"The resume matches {overall_match}% of the job description. "
            f"The candidate is best suited for {predicted_role}. "
            f"Major gaps are identified in {', '.join(missing_skills[:3])}."

    }
