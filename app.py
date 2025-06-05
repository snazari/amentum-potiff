import streamlit as st
import pdfplumber
import docx
import re
import pandas as pd
from collections import Counter
import plotly.express as px
import plotly.graph_objects as go
from io import BytesIO

# Set page config
st.set_page_config(
    page_title="AI-Powered ATS System",
    page_icon="📄",
    layout="wide"
)

# Custom CSS for darker theme with bolder fonts
st.markdown("""
<style>
    /* Main container and app background */
    .main {
        padding: 2rem;
        background-color: #1a1a1a;
    }
    .stApp {
        background-color: #0d0d0d;
        color: #ffffff;
    }
    
    /* Headers and text */
    h1, h2, h3, h4, h5, h6 {
        color: #ffffff !important;
        font-weight: 700 !important;
    }
    
    p, span, div {
        color: #e0e0e0 !important;
        font-weight: 500 !important;
    }
    
    /* Sidebar styling */
    .css-1d391kg, [data-testid="stSidebar"] {
        background-color: #1a1a1a !important;
    }
    
    .css-1d391kg p, [data-testid="stSidebar"] p {
        color: #e0e0e0 !important;
        font-weight: 600 !important;
    }
    
    /* Upload box */
    .upload-box {
        border: 2px dashed #4a90e2;
        border-radius: 10px;
        padding: 2rem;
        text-align: center;
        background-color: #262626;
    }
    
    /* Skill tags */
    .skill-tag {
        display: inline-block;
        padding: 0.35rem 0.75rem;
        margin: 0.25rem;
        background-color: #4a90e2;
        color: white;
        border-radius: 20px;
        font-size: 0.9rem;
        font-weight: 600;
    }
    
    /* Match score */
    .match-score {
        font-size: 2.5rem;
        font-weight: 800;
        color: #4ade80;
    }
    
    /* Metrics */
    [data-testid="metric-container"] {
        background-color: #262626;
        border: 1px solid #333333;
        padding: 1rem;
        border-radius: 8px;
        margin: 0.5rem 0;
    }
    
    [data-testid="metric-container"] label {
        color: #e0e0e0 !important;
        font-weight: 600 !important;
    }
    
    [data-testid="metric-container"] [data-testid="metric-value"] {
        color: #ffffff !important;
        font-weight: 700 !important;
    }
    
    /* File uploader */
    [data-testid="stFileUploadDropzone"] {
        background-color: #262626;
        border: 2px dashed #4a90e2;
    }
    
    /* Buttons */
    .stButton > button {
        background-color: #4a90e2;
        color: white;
        font-weight: 600;
        border: none;
        padding: 0.5rem 1rem;
        border-radius: 6px;
    }
    
    .stButton > button:hover {
        background-color: #357abd;
    }
    
    /* Selectbox */
    .stSelectbox > div > div {
        background-color: #262626;
        color: #ffffff;
        font-weight: 600;
    }
    
    /* Success, warning, info boxes */
    .stAlert {
        background-color: #262626;
        border: 1px solid #333333;
        color: #ffffff;
        font-weight: 600;
    }
    
    /* Download button */
    .stDownloadButton > button {
        background-color: #4a90e2;
        color: white;
        font-weight: 600;
    }
    
    /* Markdown text */
    .stMarkdown {
        color: #e0e0e0 !important;
    }
    
    /* Custom score display */
    .score-display {
        text-align: center;
        padding: 1.5rem;
        background-color: #262626;
        border-radius: 12px;
        margin: 1rem 0;
        border: 2px solid #333333;
    }
    
    .score-display h2 {
        font-weight: 800;
        margin: 0;
    }
    
    .score-display p {
        font-weight: 600;
        margin-top: 0.5rem;
    }
</style>
""", unsafe_allow_html=True)

# Title and description
st.title("AI-Powered Applicant Tracking System")
st.markdown("### Resume Parsing & Skill Matching")
st.markdown("---")

# Predefined job requirements
JOB_POSITIONS = {
    "Senior Python Developer": {
        "required_skills": ["Python", "Django", "Flask", "REST API", "PostgreSQL", "Docker", "Git", "AWS"],
        "preferred_skills": ["Machine Learning", "Kubernetes", "Redis", "Celery", "FastAPI", "Microservices"],
        "experience_years": 5,
        "description": "Looking for a senior Python developer with strong backend development skills"
    },
    "Data Scientist": {
        "required_skills": ["Python", "Machine Learning", "Deep Learning", "TensorFlow", "PyTorch", "Pandas", "NumPy", "SQL"],
        "preferred_skills": ["NLP", "Computer Vision", "Spark", "Hadoop", "AWS", "Docker", "MLOps"],
        "experience_years": 3,
        "description": "Seeking a data scientist with expertise in ML/DL and statistical analysis"
    },
    "Full Stack Developer": {
        "required_skills": ["JavaScript", "React", "Node.js", "HTML", "CSS", "MongoDB", "Express", "Git"],
        "preferred_skills": ["TypeScript", "Next.js", "GraphQL", "Docker", "AWS", "Redux", "Webpack"],
        "experience_years": 4,
        "description": "Need a full stack developer proficient in modern web technologies"
    },
    "DevOps Engineer": {
        "required_skills": ["Docker", "Kubernetes", "CI/CD", "Jenkins", "AWS", "Linux", "Terraform", "Ansible"],
        "preferred_skills": ["Python", "Bash", "Prometheus", "Grafana", "ELK Stack", "GitOps", "ArgoCD"],
        "experience_years": 4,
        "description": "Looking for a DevOps engineer to manage cloud infrastructure"
    }
}

# Common tech skills for extraction
TECH_SKILLS = [
    # Programming Languages
    "Python", "Java", "JavaScript", "TypeScript", "C++", "C#", "Ruby", "Go", "Rust", "Swift", "Kotlin",
    "PHP", "R", "MATLAB", "Scala", "Perl", "Objective-C", "Dart", "Julia", "Elixir", "Clojure",
    
    # Web Technologies
    "HTML", "CSS", "React", "Angular", "Vue.js", "Node.js", "Express", "Django", "Flask", "FastAPI",
    "Spring Boot", "Ruby on Rails", "ASP.NET", "Laravel", "Next.js", "Nuxt.js", "Gatsby", "Redux",
    "GraphQL", "REST API", "SOAP", "WebSockets", "jQuery", "Bootstrap", "Tailwind CSS", "Sass",
    
    # Databases
    "MySQL", "PostgreSQL", "MongoDB", "Redis", "Elasticsearch", "Cassandra", "Oracle", "SQL Server",
    "SQLite", "DynamoDB", "Neo4j", "CouchDB", "MariaDB", "Firestore", "RDS", "DocumentDB",
    
    # Cloud & DevOps
    "AWS", "Azure", "GCP", "Docker", "Kubernetes", "Jenkins", "GitLab CI", "GitHub Actions",
    "Terraform", "Ansible", "Puppet", "Chef", "CloudFormation", "CircleCI", "Travis CI",
    "Prometheus", "Grafana", "ELK Stack", "Datadog", "New Relic", "Nginx", "Apache",
    
    # Data Science & ML
    "Machine Learning", "Deep Learning", "TensorFlow", "PyTorch", "Keras", "Scikit-learn",
    "Pandas", "NumPy", "Matplotlib", "Seaborn", "Jupyter", "NLP", "Computer Vision",
    "Spark", "Hadoop", "Tableau", "Power BI", "Statistics", "Data Mining", "MLOps",
    
    # Other Technologies
    "Git", "Linux", "Windows Server", "Agile", "Scrum", "JIRA", "Confluence", "Microservices",
    "API Development", "Unit Testing", "Integration Testing", "CI/CD", "DevOps", "Cloud Computing",
    "Cybersecurity", "Blockchain", "IoT", "AR/VR", "Mobile Development", "Android", "iOS"
]

def extract_text_from_pdf(pdf_file):
    """Extract text from PDF file"""
    text = ""
    try:
        with pdfplumber.open(pdf_file) as pdf:
            for page in pdf.pages:
                text += page.extract_text() or ""
    except Exception as e:
        st.error(f"Error reading PDF: {str(e)}")
    return text

def extract_text_from_docx(docx_file):
    """Extract text from DOCX file"""
    text = ""
    try:
        doc = docx.Document(docx_file)
        for paragraph in doc.paragraphs:
            text += paragraph.text + "\n"
    except Exception as e:
        st.error(f"Error reading DOCX: {str(e)}")
    return text

def extract_skills_from_text(text):
    """Extract skills from resume text using pattern matching"""
    text = text.upper()
    found_skills = []
    
    for skill in TECH_SKILLS:
        # Create regex pattern for whole word matching
        pattern = r'\b' + re.escape(skill.upper()) + r'\b'
        if re.search(pattern, text):
            found_skills.append(skill)
    
    # Also extract years of experience
    experience_pattern = r'(\d+)\+?\s*(?:years?|yrs?)\s*(?:of\s*)?(?:experience|exp)'
    experience_matches = re.findall(experience_pattern, text, re.IGNORECASE)
    years_experience = max([int(match) for match in experience_matches], default=0)
    
    return found_skills, years_experience

def calculate_skill_match(candidate_skills, job_requirements):
    """Calculate match percentage between candidate skills and job requirements"""
    required_skills = [skill.upper() for skill in job_requirements["required_skills"]]
    preferred_skills = [skill.upper() for skill in job_requirements["preferred_skills"]]
    candidate_skills_upper = [skill.upper() for skill in candidate_skills]
    
    # Calculate matches
    required_matches = sum(1 for skill in required_skills if skill in candidate_skills_upper)
    preferred_matches = sum(1 for skill in preferred_skills if skill in candidate_skills_upper)
    
    # Calculate scores
    required_score = (required_matches / len(required_skills) * 100) if required_skills else 0
    preferred_score = (preferred_matches / len(preferred_skills) * 100) if preferred_skills else 0
    
    # Overall score (70% weight on required, 30% on preferred)
    overall_score = (required_score * 0.7) + (preferred_score * 0.3)
    
    return {
        "overall_score": overall_score,
        "required_score": required_score,
        "preferred_score": preferred_score,
        "required_matches": required_matches,
        "preferred_matches": preferred_matches,
        "total_required": len(required_skills),
        "total_preferred": len(preferred_skills)
    }

# Sidebar for job position selection
with st.sidebar:
    st.header("Job Position Selection")
    selected_position = st.selectbox(
        "Select Job Position",
        options=list(JOB_POSITIONS.keys()),
        index=0
    )
    
    st.markdown("### Job Requirements")
    job_req = JOB_POSITIONS[selected_position]
    
    st.markdown(f"**Description:** {job_req['description']}")
    st.markdown(f"**Experience Required:** {job_req['experience_years']}+ years")
    
    st.markdown("**Required Skills:**")
    for skill in job_req["required_skills"]:
        st.markdown(f"• {skill}")
    
    st.markdown("**Preferred Skills:**")
    for skill in job_req["preferred_skills"]:
        st.markdown(f"• {skill}")

# Main content area
col1, col2 = st.columns([1, 1])

with col1:
    st.header("Upload Resume")
    
    uploaded_file = st.file_uploader(
        "Choose a resume file",
        type=['pdf', 'docx', 'txt'],
        help="Supported formats: PDF, DOCX, TXT"
    )
    
    if uploaded_file is not None:
        # Extract text based on file type
        if uploaded_file.type == "application/pdf":
            text = extract_text_from_pdf(uploaded_file)
        elif uploaded_file.type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
            text = extract_text_from_docx(uploaded_file)
        else:  # txt file
            text = str(uploaded_file.read(), "utf-8")
        
        if text:
            st.success(f"Successfully loaded: {uploaded_file.name}")
            
            # Extract skills
            extracted_skills, years_experience = extract_skills_from_text(text)
            
            # Store in session state
            st.session_state['resume_text'] = text
            st.session_state['extracted_skills'] = extracted_skills
            st.session_state['years_experience'] = years_experience
            st.session_state['filename'] = uploaded_file.name

with col2:
    st.header("Skill Analysis")
    
    if 'extracted_skills' in st.session_state:
        st.markdown(f"**Resume:** {st.session_state['filename']}")
        st.markdown(f"**Years of Experience:** {st.session_state['years_experience']}")
        
        # Display extracted skills
        st.markdown("**Extracted Skills:**")
        skills_html = ""
        for skill in st.session_state['extracted_skills']:
            skills_html += f'<span class="skill-tag">{skill}</span>'
        st.markdown(skills_html, unsafe_allow_html=True)
        
        # Calculate match score
        match_results = calculate_skill_match(
            st.session_state['extracted_skills'],
            JOB_POSITIONS[selected_position]
        )
        
        st.markdown("### Match Results")
        
        # Display overall score with color coding
        score_color = "#4ade80" if match_results['overall_score'] >= 70 else "#fbbf24" if match_results['overall_score'] >= 50 else "#ef4444"
        st.markdown(
            f'<div class="score-display">'
            f'<h2 style="color: {score_color};">{match_results["overall_score"]:.1f}%</h2>'
            f'<p>Overall Match Score</p>'
            f'</div>',
            unsafe_allow_html=True
        )
        
        # Create metrics columns
        metric_col1, metric_col2 = st.columns(2)
        
        with metric_col1:
            st.metric(
                "Required Skills Match",
                f"{match_results['required_matches']}/{match_results['total_required']}",
                f"{match_results['required_score']:.0f}%"
            )
        
        with metric_col2:
            st.metric(
                "Preferred Skills Match",
                f"{match_results['preferred_matches']}/{match_results['total_preferred']}",
                f"{match_results['preferred_score']:.0f}%"
            )

# Visualization section
if 'extracted_skills' in st.session_state:
    st.markdown("---")
    st.header("Detailed Analysis")
    
    viz_col1, viz_col2 = st.columns(2)
    
    with viz_col1:
        # Skills gap analysis
        job_req = JOB_POSITIONS[selected_position]
        all_required_skills = job_req["required_skills"] + job_req["preferred_skills"]
        candidate_skills_upper = [skill.upper() for skill in st.session_state['extracted_skills']]
        
        skill_status = []
        for skill in all_required_skills:
            status = "Matched" if skill.upper() in candidate_skills_upper else "Missing"
            skill_type = "Required" if skill in job_req["required_skills"] else "Preferred"
            skill_status.append({
                "Skill": skill,
                "Status": status,
                "Type": skill_type
            })
        
        df_skills = pd.DataFrame(skill_status)
        
        # Create a grouped bar chart with dark theme
        fig = px.bar(
            df_skills.groupby(['Type', 'Status']).size().reset_index(name='Count'),
            x='Type',
            y='Count',
            color='Status',
            title='Skills Gap Analysis',
            color_discrete_map={'Matched': '#4ade80', 'Missing': '#ef4444'},
            template='plotly_dark'
        )
        fig.update_layout(
            plot_bgcolor='#1a1a1a',
            paper_bgcolor='#1a1a1a',
            font=dict(color='#ffffff', size=14, family="Arial Black")
        )
        st.plotly_chart(fig, use_container_width=True)
    
    with viz_col2:
        # Skill categories pie chart
        skill_categories = {
            "Languages": ["Python", "Java", "JavaScript", "TypeScript", "C++", "C#", "Ruby", "Go", "Rust", "Swift", "Kotlin", "PHP", "R"],
            "Frameworks": ["React", "Angular", "Vue.js", "Django", "Flask", "Spring Boot", "Express", "FastAPI", "Next.js"],
            "Databases": ["MySQL", "PostgreSQL", "MongoDB", "Redis", "Elasticsearch", "Cassandra", "Oracle", "SQL Server"],
            "Cloud/DevOps": ["AWS", "Azure", "GCP", "Docker", "Kubernetes", "Jenkins", "Terraform", "Ansible"],
            "Data Science": ["Machine Learning", "Deep Learning", "TensorFlow", "PyTorch", "Pandas", "NumPy", "NLP"]
        }
        
        category_counts = {}
        for category, skills in skill_categories.items():
            count = sum(1 for skill in st.session_state['extracted_skills'] if skill in skills)
            if count > 0:
                category_counts[category] = count
        
        if category_counts:
            fig_pie = px.pie(
                values=list(category_counts.values()),
                names=list(category_counts.keys()),
                title='Candidate Skills by Category',
                template='plotly_dark'
            )
            fig_pie.update_layout(
                plot_bgcolor='#1a1a1a',
                paper_bgcolor='#1a1a1a',
                font=dict(color='#ffffff', size=14, family="Arial Black")
            )
            st.plotly_chart(fig_pie, use_container_width=True)
    
    # Recommendation section
    st.markdown("### Recommendations")
    
    missing_required = [skill for skill in job_req["required_skills"] 
                       if skill.upper() not in candidate_skills_upper]
    missing_preferred = [skill for skill in job_req["preferred_skills"] 
                        if skill.upper() not in candidate_skills_upper]
    
    recommendation_col1, recommendation_col2 = st.columns(2)
    
    with recommendation_col1:
        if missing_required:
            st.warning("**Missing Required Skills:**")
            for skill in missing_required:
                st.markdown(f"• {skill}")
        else:
            st.success("All required skills matched!")
    
    with recommendation_col2:
        if missing_preferred:
            st.info("**Missing Preferred Skills:**")
            for skill in missing_preferred:
                st.markdown(f"• {skill}")
        else:
            st.success("All preferred skills matched!")
    
    # Experience check
    if st.session_state['years_experience'] < job_req['experience_years']:
        st.warning(f"The candidate has {st.session_state['years_experience']} years of experience, "
                  f"but the position requires {job_req['experience_years']}+ years.")
    else:
        st.success(f"Experience requirement met: {st.session_state['years_experience']} years")

# Sample resumes section
st.markdown("---")
st.header("Sample Resume Templates")
st.info("Don't have a resume to test? You can create sample resumes with the button below!")

if st.button("Generate Sample Resume"):
    sample_resumes = {
        "Python Developer": """John Doe
Email: john.doe@email.com | Phone: (555) 123-4567 | LinkedIn: linkedin.com/in/johndoe

PROFESSIONAL SUMMARY
Experienced Python Developer with 6+ years of experience in building scalable web applications and APIs. 
Proficient in Django, Flask, and FastAPI frameworks. Strong background in PostgreSQL, Docker, and AWS cloud services.

TECHNICAL SKILLS
Languages: Python, JavaScript, SQL, Bash
Frameworks: Django, Flask, FastAPI, React
Databases: PostgreSQL, MySQL, MongoDB, Redis
Tools: Docker, Kubernetes, Git, Jenkins, Terraform
Cloud: AWS (EC2, S3, RDS, Lambda), GCP

PROFESSIONAL EXPERIENCE
Senior Python Developer | Tech Corp | 2020-Present
• Developed RESTful APIs using FastAPI serving 1M+ requests daily
• Implemented microservices architecture using Docker and Kubernetes
• Optimized database queries reducing response time by 40%

Python Developer | StartupXYZ | 2018-2020
• Built web applications using Django and PostgreSQL
• Integrated machine learning models for recommendation system
• Implemented CI/CD pipelines using Jenkins and GitHub Actions

EDUCATION
Bachelor of Science in Computer Science | University of Technology | 2018
""",
        "Data Scientist": """Sarah Johnson
Email: sarah.j@email.com | Phone: (555) 987-6543 | GitHub: github.com/sarahj

PROFESSIONAL SUMMARY
Data Scientist with 4 years of experience in machine learning, deep learning, and statistical analysis.
Expertise in Python, TensorFlow, and PyTorch. Proven track record in NLP and computer vision projects.

TECHNICAL SKILLS
Programming: Python, R, SQL, Scala
ML/DL: TensorFlow, PyTorch, Keras, Scikit-learn
Data Tools: Pandas, NumPy, Matplotlib, Seaborn, Jupyter
Big Data: Spark, Hadoop, Hive
Cloud: AWS SageMaker, Azure ML
Specializations: NLP, Computer Vision, MLOps

PROFESSIONAL EXPERIENCE
Data Scientist | AI Solutions Inc. | 2021-Present
• Developed deep learning models for image classification achieving 95% accuracy
• Built NLP pipeline for sentiment analysis processing 100K+ documents daily
• Implemented MLOps practices reducing model deployment time by 60%

Junior Data Scientist | DataCorp | 2020-2021
• Created machine learning models for customer churn prediction
• Performed statistical analysis on large datasets using Pandas and NumPy
• Visualized insights using Tableau and Power BI

EDUCATION
Master of Science in Data Science | Data University | 2020
Bachelor of Science in Statistics | Stats College | 2018
""",
        "Full Stack Developer": """Michael Chen
Email: m.chen@email.com | Portfolio: michaelchen.dev

PROFESSIONAL SUMMARY
Full Stack Developer with 5 years of experience in modern web development.
Expert in JavaScript, React, Node.js, and MongoDB. Passionate about creating responsive and user-friendly applications.

TECHNICAL SKILLS
Frontend: JavaScript, TypeScript, React, Redux, Next.js, HTML, CSS, Tailwind CSS
Backend: Node.js, Express, GraphQL, REST API
Databases: MongoDB, PostgreSQL, Redis
Tools: Git, Docker, Webpack, Jest, CI/CD
Cloud: AWS, Vercel, Netlify

PROFESSIONAL EXPERIENCE
Senior Full Stack Developer | WebTech Solutions | 2021-Present
• Led development of e-commerce platform using React and Node.js
• Implemented GraphQL API reducing data over-fetching by 50%
• Mentored junior developers and conducted code reviews

Full Stack Developer | Digital Agency | 2019-2021
• Built responsive web applications using React and Express
• Integrated third-party APIs and payment gateways
• Optimized application performance improving load times by 35%

EDUCATION
Bachelor of Science in Computer Science | Tech University | 2019
"""
    }
    
    # Create download buttons for sample resumes
    for title, content in sample_resumes.items():
        col1, col2, col3 = st.columns([2, 1, 1])
        with col1:
            st.markdown(f"**{title} Resume**")
        with col2:
            st.download_button(
                label="Download TXT",
                data=content,
                file_name=f"{title.replace(' ', '_')}_Resume.txt",
                mime="text/plain"
            )

st.markdown("---")
st.markdown(
    "<div style='text-align: center; color: #999999; padding: 2rem; font-weight: 600;'>"
    "Built with Streamlit | AI-Powered ATS System"
    "</div>",
    unsafe_allow_html=True
) 