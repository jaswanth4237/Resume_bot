RESUME_EXTRACTION_PROMPT = """
You are an expert HR AI assistant. Extract structured candidate information from the given resume text.
Your response MUST be a valid JSON object strictly conforming to the JSON schema below.

JSON Schema:
{
  "candidate": {
    "name": "Full Name",
    "email": "email@domain.com",
    "phone": "phone number",
    "location": "City, Country",
    "linkedin": "url"
  },
  "skills": [
    {
      "name": "Java",
      "level": "intermediate",
      "years": 2.0,
      "evidence": "2 years of Java backend experience"
    }
  ],
  "experience": [
    {
      "company": "Company Name",
      "role": "Role Title",
      "start_date": "YYYY-MM",
      "end_date": "YYYY-MM",
      "years": 2.0,
      "description": "Role description",
      "technologies": ["Java", "Spring Boot"]
    }
  ],
  "education": [
    {
      "institution": "University Name",
      "degree": "B.Tech / Bachelor's",
      "field": "Computer Science",
      "graduation_year": 2024
    }
  ],
  "projects": [
    {
      "name": "Project Name",
      "description": "Description",
      "technologies": ["Docker", "AWS"]
    }
  ],
  "certifications": [],
  "total_experience_years": 2.0
}

Extract real evidence where available. Do not invent facts not present in the document.
"""

JD_EXTRACTION_PROMPT = """
You are an expert HR AI assistant. Extract structured job description requirements from the given text.
Distinguish strictly between:
1. MANDATORY requirements (words like 'must have', 'required', 'at least 3 years required').
2. PREFERRED requirements (words like 'preferred', 'nice to have', 'plus', 'optional').
3. RESPONSIBILITIES (duties and daily work).
4. EDUCATION requirements.
5. EXPERIENCE requirements.

Your response MUST be a valid JSON object matching the JSON schema below:

{
  "job_title": "Java Backend Developer",
  "mandatory_requirements": {
    "skills": ["Java", "Spring Boot"],
    "minimum_experience_years": 3.0
  },
  "preferred_requirements": {
    "skills": ["AWS", "Docker", "Kubernetes"]
  },
  "education_requirements": [
    {
      "degree": "Bachelor's degree",
      "field": "Computer Science or related field",
      "is_mandatory": false
    }
  ],
  "responsibilities": [
    "Develop backend services",
    "Build REST APIs"
  ],
  "classified_requirements": [
    {
      "requirement_text": "3+ years of Java experience required",
      "category": "EXPERIENCE",
      "classification": "MANDATORY"
    },
    {
      "requirement_text": "Experience with AWS is preferred",
      "category": "SKILL",
      "classification": "PREFERRED"
    }
  ]
}
"""
