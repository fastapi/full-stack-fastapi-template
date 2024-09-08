from pydantic import BaseModel as PyDanticModel, Field, ValidationError
from typing import List, Optional, Dict


class PersonalDetails(PyDanticModel):
    first_name: str = Field(default="", description="The first name of the person.")
    last_name: str = Field(default="", description="The last name of the person.")
    phone_number: Optional[str] = Field(default=None, description="The phone number of the person.")
    linkedin_url: Optional[str] = Field(default=None, description="The url of the linkedin profile of the person.")
    email_address: Optional[str] = Field(default=None, description="The email address of the person.")
    nationality: Optional[str] = Field(default=None, description="The nationality of the person.")
    professional_summary: Optional[str] = Field(default=None, description="The professional summary or the profile section of resume of the person")


class Education(PyDanticModel):
    degree: str = Field(default="", description="The degree obtained or expected.")
    institution: str = Field(default="", description="The university, college, or educational institution visited.")
    field_of_study: str = Field(default="", description="The field of study.")
    country: Optional[str] = Field(default=None, description="The country of the institution.")
    grade: Optional[str] = Field(default=None, description="The grade achieved or expected.")
    start_date: Optional[str] = Field(default=None, description="When the study started.")
    end_date: Optional[str] = Field(default=None, description="When the study ended.")


class WorkExperience(PyDanticModel):
    company: str = Field(default="", description="The company name of the work experience.")
    job_title: str = Field(default="", description="The job title.")
    description: Optional[str] = Field(default=None, description="The job or role description.")
    start_date: Optional[str] = Field(default=None, description="When the job started.")
    end_date: Optional[str] = Field(default=None, description="When the job ended.")
    notable_contributions: List[str] = Field(default=[], description="notable contributions in the work experience")


class Project(PyDanticModel):
    name: str = Field(default="", description="The name of the project")
    description: Optional[str] = Field(default=None, description="The description of the project")
    technologies: Optional[str] = Field(default=None, description="the technologies used in the project")
    role: Optional[str] = Field(default=None, description="The role of the person in the project")

class Certification(PyDanticModel):
    title: str = Field(default="", description="Title of the certificate")
    certifying_body: Optional[str] = Field(default=None, description="The text or body of the certificate")
    date: Optional[str] = Field(default=None, description="The Date of the certificate")

class Publication(PyDanticModel):
    title: str = Field(default="", description="The title of the publication")
    co_authors: List[str] = Field(default=[], description="The list of other authors of the publication")
    date: Optional[str] = Field(default=None, description="the date of publication")

class Award(PyDanticModel):
    title: str = Field(default="", description="Award Title")
    awarding_body: Optional[str] = Field(default=None, description="the text or body of award")
    date: Optional[str] = Field(default=None, description="the date of award")

class VolunteerExperience(PyDanticModel):
    organization: str = Field(default="", description="the organization name of volunteer experience")
    description: Optional[str] = Field(default=None, description="the description of volunteer experience")
    role: Optional[str] = Field(default=None, description="role of the person in the volunteer experience")
    start_date: Optional[str] = Field(default=None, description="the start date of the volunteer experience")
    end_date: Optional[str] = Field(default=None, description="the end date of the volunteer experience")

class Resume(PyDanticModel):
    personal_details: PersonalDetails
    education: List[Education] = []
    work_experience: List[WorkExperience] = []
    projects: List[Project] = []
    skills: List[str] = []
    certifications: List[Certification] = []
    publications: List[Publication] = []
    awards: List[Award] = []
    volunteer_experience: List[VolunteerExperience] = []
    languages: List[str] = []
    interests: List[str] = []