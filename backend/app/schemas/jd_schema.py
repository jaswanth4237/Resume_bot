from typing import List, Optional
from pydantic import BaseModel, Field


class MandatoryRequirements(BaseModel):
    skills: List[str] = Field(default_factory=list, description="Explicitly mandatory/required skills")
    minimum_experience_years: float = Field(default=0.0, description="Minimum mandatory experience years required")


class PreferredRequirements(BaseModel):
    skills: List[str] = Field(default_factory=list, description="Preferred/nice-to-have skills")


class EducationRequirement(BaseModel):
    degree: str = Field(default="Bachelor's")
    field: Optional[str] = Field(default="Computer Science")
    is_mandatory: bool = Field(default=False)


class RequirementClassification(BaseModel):
    requirement_text: str
    category: str = Field(..., description="SKILL, EXPERIENCE, EDUCATION, RESPONSIBILITY")
    classification: str = Field(..., description="MANDATORY, PREFERRED, RESPONSIBILITY, EDUCATION, EXPERIENCE")


class JDSchema(BaseModel):
    job_title: str = Field(default="Software Engineer", description="Target job title")
    mandatory_requirements: MandatoryRequirements = Field(default_factory=MandatoryRequirements)
    preferred_requirements: PreferredRequirements = Field(default_factory=PreferredRequirements)
    education_requirements: List[EducationRequirement] = Field(default_factory=list)
    responsibilities: List[str] = Field(default_factory=list, description="Key duties and responsibilities")
    classified_requirements: List[RequirementClassification] = Field(default_factory=list)
