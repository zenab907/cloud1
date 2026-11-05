import re
import fitz
from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title="AI Career Match API",
    version="1.5.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------------------------------------------------------------------------
# Skills database: category -> {skill name: [aliases]}
# Aliases are matched in lowercase as whole words.
# ---------------------------------------------------------------------------
SKILLS_BY_CATEGORY = {
    "Programming Languages": {
        "Python": ["python"],
        "Java": ["java"],
        "JavaScript": ["javascript", "js", "ecmascript", "es6"],
        "TypeScript": ["typescript"],
        "C++": ["c++", "cpp"],
        "C#": ["c#", "csharp"],
        "Go": ["golang"],
        "PHP": ["php"],
        "Ruby": ["ruby"],
        "Kotlin": ["kotlin"],
        "Dart": ["dart"],
        "Rust": ["rust"],
        "Scala": ["scala"],
        "MATLAB": ["matlab"],
        "Bash": ["bash", "shell scripting"],
    },
    "Web Development": {
        "HTML": ["html", "html5"],
        "CSS": ["css", "css3"],
        "React": ["react", "react.js", "reactjs"],
        "Next.js": ["next.js", "nextjs"],
        "Vue.js": ["vue", "vue.js", "vuejs"],
        "Angular": ["angular", "angularjs"],
        "Node.js": ["node.js", "nodejs", "node js"],
        "Express.js": ["express.js", "expressjs"],
        "Tailwind CSS": ["tailwind", "tailwindcss", "tailwind css"],
        "Bootstrap": ["bootstrap"],
        "REST API": ["rest api", "rest apis", "restful api", "restful apis"],
        "GraphQL": ["graphql"],
        "FastAPI": ["fastapi", "fast api", "fast-api"],
        "Django": ["django"],
        "Flask": ["flask"],
        "Spring Boot": ["spring boot", "springboot"],
        ".NET": [".net", "dotnet", "asp.net"],
        "Laravel": ["laravel"],
        "Responsive Design": ["responsive design"],
    },
    "Databases": {
        "SQL": ["sql", "t-sql", "pl/sql"],
        "MySQL": ["mysql"],
        "PostgreSQL": ["postgresql", "postgres"],
        "SQLite": ["sqlite"],
        "SQL Server": ["sql server", "mssql"],
        "Oracle": ["oracle"],
        "NoSQL": ["nosql"],
        "MongoDB": ["mongodb"],
        "Redis": ["redis"],
        "Firebase": ["firebase"],
        "Elasticsearch": ["elasticsearch", "elastic search"],
    },
    "Data & AI": {
        "Machine Learning": ["machine learning"],
        "Deep Learning": ["deep learning"],
        "Artificial Intelligence": ["artificial intelligence"],
        "Generative AI": ["generative ai"],
        "LLMs": ["llm", "llms", "large language model", "large language models"],
        "NLP": ["nlp", "natural language processing"],
        "Computer Vision": ["computer vision"],
        "Data Analysis": ["data analysis", "data analytics"],
        "Data Science": ["data science"],
        "Data Visualization": ["data visualization", "data visualisation"],
        "Statistics": ["statistics", "statistical analysis"],
        "Pandas": ["pandas"],
        "NumPy": ["numpy"],
        "Scikit-learn": ["scikit-learn", "scikit learn", "sklearn"],
        "TensorFlow": ["tensorflow"],
        "PyTorch": ["pytorch", "torch"],
        "Keras": ["keras"],
        "OpenCV": ["opencv"],
        "Matplotlib": ["matplotlib"],
        "Excel": ["excel"],
        "Power BI": ["power bi", "powerbi"],
        "Tableau": ["tableau"],
        "ETL": ["etl"],
        "Big Data": ["big data"],
        "Spark": ["apache spark", "pyspark"],
    },
    "Cloud & DevOps": {
        "Docker": ["docker"],
        "Kubernetes": ["kubernetes", "k8s"],
        "AWS": ["aws", "amazon web services"],
        "Azure": ["azure", "microsoft azure"],
        "Google Cloud": ["google cloud", "gcp"],
        "Cloud Computing": ["cloud computing"],
        "Linux": ["linux"],
        "CI/CD": ["ci/cd", "cicd", "continuous integration"],
        "Jenkins": ["jenkins"],
        "Terraform": ["terraform"],
        "GitHub Actions": ["github actions"],
        "Nginx": ["nginx"],
        "Microservices": ["microservices", "microservice"],
    },
    "Tools & Practices": {
        "Git": ["git"],
        "GitHub": ["github"],
        "Jira": ["jira"],
        "Postman": ["postman"],
        "Figma": ["figma"],
        "Agile": ["agile", "scrum"],
        "Unit Testing": ["unit testing", "unit tests", "pytest", "jest"],
        "OOP": ["oop", "object-oriented", "object oriented"],
        "Data Structures & Algorithms": ["data structures", "algorithms"],
        "Cybersecurity": ["cybersecurity", "cyber security", "information security"],
    },
    "Soft Skills": {
        "Communication": ["communication"],
        "Teamwork": ["teamwork", "collaboration", "team player"],
        "Problem Solving": ["problem solving", "problem-solving"],
        "Project Management": ["project management"],
        "Leadership": ["leadership"],
        "Time Management": ["time management"],
        "Critical Thinking": ["critical thinking"],
        "Adaptability": ["adaptability"],
    },
}

# Short abbreviations that must be written in capitals to count
# (so the word "ai" or "ml" inside normal text is not treated as a skill).
CASE_SENSITIVE_ALIASES = {
    "Machine Learning": ["ML"],
    "Artificial Intelligence": ["AI"],
}

# If the CV shows the skill on the left, it also shows the skills on the right.
IMPLIED_SKILLS = {
    "MySQL": ["SQL"],
    "PostgreSQL": ["SQL"],
    "SQLite": ["SQL"],
    "SQL Server": ["SQL"],
    "React": ["JavaScript"],
    "Next.js": ["React"],
    "Vue.js": ["JavaScript"],
    "Node.js": ["JavaScript"],
    "Express.js": ["Node.js"],
    "TypeScript": ["JavaScript"],
    "Django": ["Python"],
    "Flask": ["Python"],
    "FastAPI": ["Python"],
    "Pandas": ["Python"],
    "NumPy": ["Python"],
    "Scikit-learn": ["Python", "Machine Learning"],
    "TensorFlow": ["Machine Learning"],
    "PyTorch": ["Machine Learning"],
    "Keras": ["Machine Learning"],
    "Deep Learning": ["Machine Learning"],
    "Machine Learning": ["Artificial Intelligence"],
    "Generative AI": ["Artificial Intelligence"],
    "LLMs": ["Artificial Intelligence"],
    "Spring Boot": ["Java"],
    "Tailwind CSS": ["CSS"],
    "Bootstrap": ["CSS"],
    "GitHub": ["Git"],
    "GitHub Actions": ["Git", "CI/CD"],
}

# Flat lookups built from the table above
SKILL_ALIASES = {}
SKILL_CATEGORY = {}
for _category, _skills in SKILLS_BY_CATEGORY.items():
    for _skill, _aliases in _skills.items():
        SKILL_ALIASES[_skill] = _aliases
        SKILL_CATEGORY[_skill] = _category

CATEGORY_TIPS = {
    "Programming Languages": (
        "add a project or job where you used it and mention what you built"
    ),
    "Web Development": (
        "add a project that uses it and link to the code or a live demo"
    ),
    "Databases": (
        "describe a project where you designed or queried data with it"
    ),
    "Data & AI": (
        "add a project, course, or dataset where you applied it, "
        "and mention the result"
    ),
    "Cloud & DevOps": (
        "mention where you deployed or managed something with it "
        "(project, internship, or course)"
    ),
    "Tools & Practices": (
        "mention how you used it in a team or project"
    ),
    "Soft Skills": (
        "show it with a concrete example, such as leading or "
        "coordinating a team project"
    ),
}


# ---------------------------------------------------------------------------
# Text helpers
# ---------------------------------------------------------------------------
def normalize_spaces(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip()


def alias_pattern(alias: str) -> str:
    return r"(?<![A-Za-z0-9])" + re.escape(alias) + r"(?![A-Za-z0-9])"


def count_mentions(skill: str, lowered: str, original: str) -> int:
    total = 0
    for alias in SKILL_ALIASES[skill]:
        total += len(re.findall(alias_pattern(alias.lower()), lowered))
    for alias in CASE_SENSITIVE_ALIASES.get(skill, []):
        total += len(re.findall(alias_pattern(alias), original))
    return total


def find_skills(text: str) -> dict:
    """Returns {skill: number_of_mentions} for every skill found in the text."""
    original = normalize_spaces(text)
    lowered = original.lower()
    found = {}
    for skill in SKILL_ALIASES:
        mentions = count_mentions(skill, lowered, original)
        if mentions > 0:
            found[skill] = mentions
    return found


def expand_implied(skills: set) -> set:
    expanded = set(skills)
    changed = True
    while changed:
        changed = False
        for skill in list(expanded):
            for implied in IMPLIED_SKILLS.get(skill, []):
                if implied not in expanded:
                    expanded.add(implied)
                    changed = True
    return expanded


# ---------------------------------------------------------------------------
# Suggestions
# ---------------------------------------------------------------------------
def check_cv_structure(cv_text: str) -> list:
    lowered = cv_text.lower()
    word_count = len(cv_text.split())
    tips = []

    if not re.search(r"[\w.+-]+@[\w-]+\.[\w.-]+", cv_text):
        tips.append(
            "We could not find an email address in your CV. "
            "Make sure your contact details are clearly visible at the top."
        )
    if "project" not in lowered:
        tips.append(
            "We could not find a Projects section. Adding 2-3 projects "
            "with the tools you used is one of the best ways to show your skills."
        )
    if not any(w in lowered for w in ("summary", "objective", "profile", "about me")):
        tips.append(
            "Consider adding a short professional summary (2-3 lines) "
            "at the top that matches the job you are applying for."
        )
    if word_count < 150:
        tips.append(
            "Your CV looks quite short. Add more detail about your "
            "experience, projects, and education."
        )
    elif word_count > 1000:
        tips.append(
            "Your CV is quite long. Most recruiters prefer 1-2 pages "
            "focused on the most relevant experience."
        )
    return tips


def build_suggestions(
    missing_details: list,
    extra_skills: list,
    match_score: int,
    cv_text: str,
) -> list:
    suggestions = []

    # Missing skills, most important first (mentioned most in the job post)
    ordered = sorted(missing_details, key=lambda d: -d["mentions"])
    for item in ordered[:3]:
        skill = item["skill"]
        tip = CATEGORY_TIPS.get(item["category"], "mention where you used it")
        repeated = (
            f" It appears {item['mentions']} times in the job description."
            if item["mentions"] > 1 else ""
        )
        suggestions.append(
            f"{skill} is required for this job.{repeated} "
            f"If you have real experience with it, {tip}."
        )

    remaining = [d["skill"] for d in ordered[3:]]
    if remaining:
        suggestions.append(
            "Other required skills not found in your CV: "
            + ", ".join(remaining)
            + ". Add only the ones you genuinely have."
        )

    if match_score == 100:
        suggestions.append(
            "Your CV covers every skill detected in the job description. "
            "Focus on showing measurable results for each one."
        )

    if extra_skills:
        suggestions.append(
            "Your CV also lists skills this job does not mention ("
            + ", ".join(extra_skills[:6])
            + "). Keep the most relevant ones near the top."
        )

    suggestions.extend(check_cv_structure(cv_text))
    return suggestions


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------
@app.get("/")
def home():
    return {
        "status": "ok",
        "message": "AI Career Match API is running",
        "version": "1.5.0"
    }


@app.post("/analyze")
async def analyze_cv(
    cv: UploadFile = File(...),
    job_description: str = Form(...)
):
    if not cv.filename or not cv.filename.lower().endswith(".pdf"):
        raise HTTPException(
            status_code=400,
            detail="Please upload a PDF file."
        )

    if not job_description.strip():
        raise HTTPException(
            status_code=400,
            detail="Job description cannot be empty."
        )

    file_bytes = await cv.read()

    if len(file_bytes) > 10 * 1024 * 1024:
        raise HTTPException(
            status_code=400,
            detail="PDF size must not exceed 10 MB."
        )

    try:
        document = fitz.open(
            stream=file_bytes,
            filetype="pdf"
        )
        cv_text = " ".join(
            page.get_text() for page in document
        )
        document.close()

    except Exception:
        raise HTTPException(
            status_code=400,
            detail="Could not read this PDF file."
        )

    if len(cv_text.strip()) < 30:
        raise HTTPException(
            status_code=400,
            detail="No readable text found. Please upload a text-based PDF."
        )

    # Extract skills (with how many times each one is mentioned)
    cv_found = find_skills(cv_text)
    job_found = find_skills(job_description)

    cv_skills = list(cv_found)
    required_skills = list(job_found)

    if not required_skills:
        raise HTTPException(
            status_code=400,
            detail="No supported skills were found in the job description."
        )

    # Skills the CV proves, including implied ones (e.g. MySQL -> SQL)
    cv_effective = expand_implied(set(cv_skills))

    matched_skills = [s for s in required_skills if s in cv_effective]
    missing_skills = [s for s in required_skills if s not in cv_effective]
    extra_skills = [s for s in cv_skills if s not in required_skills]

    match_score = round(len(matched_skills) / len(required_skills) * 100)

    skill_details = []
    missing_details = []
    for skill in required_skills:
        matched = skill in cv_effective
        detail = {
            "skill": skill,
            "category": SKILL_CATEGORY[skill],
            "mentions": job_found[skill],
            "status": "Matched" if matched else "Missing",
        }
        skill_details.append(detail)
        if not matched:
            missing_details.append(detail)

    suggestions = build_suggestions(
        missing_details, extra_skills, match_score, cv_text
    )

    return {
        "match_score": match_score,

        "cv_skills": cv_skills,
        "required_skills": required_skills,

        "matched_skills": matched_skills,
        "missing_skills": missing_skills,
        "extra_skills": extra_skills,

        "skill_details": skill_details,

        "statistics": {
            "total_required": len(required_skills),
            "total_matched": len(matched_skills),
            "total_missing": len(missing_skills),
            "total_extra": len(extra_skills),
            "cv_total_skills": len(cv_skills)
        },

        "suggestions": suggestions,

        "word_count": len(cv_text.split()),

        "analysis_method": (
            "Skill keyword matching with aliases and implied skills"
        ),

        "note": (
            "Educational estimate based on skill keyword "
            "matching; not a validated hiring score."
        )
    }
