from typing import List, Optional
from pydantic import BaseModel, Field


class CandidateInfo(BaseModel):
    name: str = Field(default="Candidate", description="Full name of candidate")
    email: Optional[str] = None
    phone: Optional[str] = None
    location: Optional[str] = None
    linkedin: Optional[str] = None


class SkillItem(BaseModel):
    name: str = Field(..., description="Name of skill/technology")
    level: Optional[str] = Field(default="intermediate", description="beginner, intermediate, advanced, expert")
    years: Optional[float] = Field(default=0.0, description="Years of experience with skill")
    evidence: Optional[str] = Field(default=None, description="Direct quote or snippet showing skill usage")


class ExperienceItem(BaseModel):
    company: str = Field(default="Unknown Company")
    role: str = Field(default="Software Engineer")
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    years: float = Field(default=0.0, description="Years in this role")
    description: Optional[str] = None
    technologies: List[str] = Field(default_factory=list)


class EducationItem(BaseModel):
    institution: str = Field(default="Unknown Institution")
    degree: str = Field(default="Bachelor's")
    field: Optional[str] = Field(default="Computer Science")
    graduation_year: Optional[int] = None


class ProjectItem(BaseModel):
    name: str = Field(default="Project")
    description: str = Field(default="")
    technologies: List[str] = Field(default_factory=list)


class CertificationItem(BaseModel):
    name: str
    issuer: Optional[str] = None
    year: Optional[int] = None


class ResumeSchema(BaseModel):
    candidate: CandidateInfo = Field(default_factory=CandidateInfo)
    skills: List[SkillItem] = Field(default_factory=list)
    experience: List[ExperienceItem] = Field(default_factory=list)
    education: List[EducationItem] = Field(default_factory=list)
    projects: List[ProjectItem] = Field(default_factory=list)
    certifications: List[CertificationItem] = Field(default_factory=list)
    total_experience_years: float = Field(default=0.0, description="Total years of experience across all roles")
