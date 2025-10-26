import re
import logging

logger = logging.getLogger(__name__)

# Optional dependencies
try:
    import nltk
    from nltk.tokenize import word_tokenize
    from nltk.corpus import stopwords
    NLTK_AVAILABLE = True
except Exception:
    NLTK_AVAILABLE = False
    word_tokenize = None
    stopwords = None

try:
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.metrics.pairwise import cosine_similarity
    SKLEARN_AVAILABLE = True
except Exception:
    SKLEARN_AVAILABLE = False
    TfidfVectorizer = None
    cosine_similarity = None

# Download NLTK resources if available
if NLTK_AVAILABLE:
    try:
        nltk.download('punkt', quiet=True)
        nltk.download('stopwords', quiet=True)
    except Exception as e:
        logger.error(f"Error downloading NLTK resources: {str(e)}")

# Basic fallback stopwords if NLTK is unavailable
FALLBACK_STOPWORDS = {
    'the','a','an','and','or','but','if','while','with','without','to','from','of','in','on','for','by','as','at','is','are','was','were','be','been','being','this','that','these','those','it','its','into'
}

def preprocess_text(text):
    """Preprocess text for keyword matching"""
    if not text:
        return ""
    # Convert to lowercase
    text = text.lower()
    # Remove special characters and numbers
    text = re.sub(r'[^\w\s]', ' ', text)
    text = re.sub(r'\d+', ' ', text)

    if NLTK_AVAILABLE and word_tokenize and stopwords:
        try:
            tokens = word_tokenize(text)
            stop_words = set(stopwords.words('english'))
            tokens = [token for token in tokens if token not in stop_words]
        except Exception:
            tokens = re.findall(r'\b\w+\b', text)
            tokens = [t for t in tokens if t not in FALLBACK_STOPWORDS]
    else:
        tokens = re.findall(r'\b\w+\b', text)
        tokens = [t for t in tokens if t not in FALLBACK_STOPWORDS]

    return ' '.join(tokens)

def calculate_match_score(resume_text, job_description, job_requirements=None):
    """Calculate match score between resume and job"""
    try:
        processed_resume = preprocess_text(resume_text)
        processed_job = preprocess_text(job_description)
        if job_requirements:
            processed_job += " " + preprocess_text(job_requirements)

        if SKLEARN_AVAILABLE and TfidfVectorizer and cosine_similarity:
            vectorizer = TfidfVectorizer()
            tfidf_matrix = vectorizer.fit_transform([processed_resume, processed_job])
            similarity = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])[0][0]
            match_score = similarity * 100
            return match_score
        else:
            # Fallback: Jaccard similarity on token sets
            resume_set = set(processed_resume.split())
            job_set = set(processed_job.split())
            if not resume_set or not job_set:
                return 0.0
            intersection = len(resume_set & job_set)
            union = len(resume_set | job_set)
            return (intersection / union) * 100.0
    except Exception as e:
        logger.error(f"Error calculating match score: {str(e)}")
        return 0.0

def extract_skills_from_resume(resume_text):
    """Extract skills from resume text"""
    try:
        common_skills = [
            'python', 'java', 'javascript', 'react', 'angular', 'vue', 'node', 'django',
            'flask', 'spring', 'sql', 'nosql', 'mongodb', 'postgresql', 'mysql', 'oracle',
            'aws', 'azure', 'gcp', 'docker', 'kubernetes', 'ci/cd', 'git', 'agile', 'scrum',
            'machine learning', 'data science', 'ai', 'devops', 'frontend', 'backend',
            'fullstack', 'mobile', 'android', 'ios', 'swift', 'kotlin', 'react native',
            'flutter', 'ui/ux', 'html', 'css', 'sass', 'less', 'bootstrap', 'tailwind',
            'typescript', 'c#', 'c++', 'php', 'ruby', 'rails', 'go', 'rust', 'scala'
        ]
        processed_text = preprocess_text(resume_text).lower()
        found_skills = []
        for skill in common_skills:
            if re.search(r'\b' + re.escape(skill) + r'\b', processed_text):
                found_skills.append(skill)
        return found_skills
    except Exception as e:
        logger.error(f"Error extracting skills: {str(e)}")
        return []

def extract_experience_from_resume(resume_text):
    """Extract work experience from resume text"""
    try:
        experience_patterns = [
            r'(?:work|professional)\s+experience(.*?)(?:education|skills|projects|references)',
            r'experience(.*?)(?:education|skills|projects|references)'
        ]
        experience_text = ""
        for pattern in experience_patterns:
            match = re.search(pattern, resume_text, re.IGNORECASE | re.DOTALL)
            if match:
                experience_text = match.group(1).strip()
                break
        if not experience_text:
            return []
        positions = []
        position_patterns = [
            r'(.*?)(?:at|@)\s+(.*?)(?:\n|$)',
            r'(.*?)\s+-\s+(.*?)(?:\n|$)'
        ]
        for pattern in position_patterns:
            matches = re.findall(pattern, experience_text)
            for match in matches:
                if len(match) >= 2:
                    position = match[0].strip()
                    company = match[1].strip()
                    positions.append({'position': position,'company': company})
        return positions
    except Exception as e:
        logger.error(f"Error extracting experience: {str(e)}")
        return []

def find_matching_jobs(resume, jobs, threshold=60.0):
    """Find matching jobs for a resume"""
    try:
        matching_jobs = []
        for job in jobs:
            match_score = calculate_match_score(
                resume.parsed_content,
                job.description,
                job.requirements
            )
            if match_score >= threshold:
                matching_jobs.append({'job': job,'match_score': match_score})
        matching_jobs.sort(key=lambda x: x['match_score'], reverse=True)
        return matching_jobs
    except Exception as e:
        logger.error(f"Error finding matching jobs: {str(e)}")
        return []