import json
import os
import logging
from typing import List, Dict, Any
from app.matching.skill_normalizer import SkillNormalizer

logger = logging.getLogger(__name__)


class CourseService:
    _courses_catalog: List[Dict[str, Any]] = []

    @classmethod
    def load_catalog(cls, data_path: str = "data/courses.json"):
        possible_paths = [
            data_path,
            os.path.join(os.path.dirname(__file__), "../../../data/courses.json"),
            os.path.join(os.getcwd(), "data/courses.json")
        ]
        for path in possible_paths:
            if os.path.exists(path):
                try:
                    with open(path, "r", encoding="utf-8") as f:
                        cls._courses_catalog = json.load(f)
                    return
                except Exception as e:
                    logger.warning(f"Error loading course catalog: {e}")

        # Built-in catalog
        cls._courses_catalog = [
            {"skill": "Docker", "title": "Docker Essentials", "platform": "Coursera", "level": "Beginner", "url": "https://www.coursera.org/learn/docker-essentials", "duration": "6 hours"},
            {"skill": "AWS", "title": "AWS Cloud Fundamentals", "platform": "AWS Training", "level": "Beginner", "url": "https://aws.amazon.com/training/", "duration": "8 hours"},
            {"skill": "AWS", "title": "AWS Developer Learning Path", "platform": "AWS Training", "level": "Intermediate", "url": "https://aws.amazon.com/training/learning-paths/developer/", "duration": "20 hours"},
            {"skill": "Kubernetes", "title": "Kubernetes for Beginners", "platform": "edX", "level": "Beginner", "url": "https://www.edx.org/learn/kubernetes", "duration": "12 hours"},
            {"skill": "Kubernetes", "title": "Kubernetes Administration", "platform": "Linux Foundation", "level": "Advanced", "url": "https://training.linuxfoundation.org/training/kubernetes-fundamentals/", "duration": "35 hours"},
            {"skill": "Microservices", "title": "Microservices Architecture", "platform": "Pluralsight", "level": "Intermediate", "url": "https://www.pluralsight.com/courses/microservices-architectural-design-patterns", "duration": "5 hours"},
            {"skill": "Spring Boot", "title": "Building Microservices with Spring Boot", "platform": "Spring Academy", "level": "Intermediate", "url": "https://spring.academy/courses/building-a-rest-api-with-spring-boot", "duration": "10 hours"},
            {"skill": "Spring Boot", "title": "Spring Boot 3 & Spring 6", "platform": "Udemy", "level": "Beginner", "url": "https://www.udemy.com/course/spring-hibernate-tutorial/", "duration": "45 hours"},
            {"skill": "Java", "title": "Java Programming Masterclass", "platform": "Udemy", "level": "Beginner", "url": "https://www.udemy.com/course/java-the-complete-java-developer-course/", "duration": "80 hours"},
            {"skill": "Python", "title": "Python for Everybody", "platform": "Coursera", "level": "Beginner", "url": "https://www.coursera.org/specializations/python", "duration": "20 hours"},
            {"skill": "REST API", "title": "API Design and Fundamentals", "platform": "Coursera", "level": "Beginner", "url": "https://www.coursera.org/learn/api-development", "duration": "8 hours"},
            {"skill": "PostgreSQL", "title": "Learn PostgreSQL", "platform": "freeCodeCamp", "level": "Beginner", "url": "https://www.youtube.com/watch?v=qw--VYLpxG4", "duration": "4 hours"},
            {"skill": "MongoDB", "title": "MongoDB Basics", "platform": "MongoDB University", "level": "Beginner", "url": "https://learn.mongodb.com/learning-paths/mongodb-python-developer-path", "duration": "6 hours"},
            {"skill": "Redis", "title": "Redis University", "platform": "Redis", "level": "Beginner", "url": "https://university.redis.com/", "duration": "8 hours"},
            {"skill": "CI/CD", "title": "GitHub Actions CI/CD", "platform": "GitHub Learning", "level": "Beginner", "url": "https://skills.github.com/", "duration": "3 hours"},
            {"skill": "GCP", "title": "Google Cloud Fundamentals", "platform": "Google Cloud", "level": "Beginner", "url": "https://cloud.google.com/training/", "duration": "10 hours"},
            {"skill": "Azure", "title": "Microsoft Azure Fundamentals", "platform": "Microsoft Learn", "level": "Beginner", "url": "https://learn.microsoft.com/en-us/training/paths/azure-fundamentals/", "duration": "10 hours"},
        ]

    @classmethod
    def get_recommendations_for_gaps(cls, gaps: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        if not cls._courses_catalog:
            cls.load_catalog()

        recommendations = []
        seen_titles = set()
        gap_skills = {
            SkillNormalizer.normalize(g["skill"]).lower()
            for g in gaps
            if g["gap_type"] in ["MISSING_SKILL", "PARTIAL_SKILL"]
        }

        for course in cls._courses_catalog:
            course_skill = SkillNormalizer.normalize(course.get("skill", "")).lower()
            matched = course_skill in gap_skills or any(
                gs in course_skill or course_skill in gs for gs in gap_skills
            )
            if matched and course["title"] not in seen_titles:
                seen_titles.add(course["title"])
                matched_gap = next(
                    (gap for gap in gap_skills if gap in course_skill or course_skill in gap),
                    course_skill,
                )
                recommendation = dict(course)
                recommendation["gap_skill"] = matched_gap
                recommendations.append(recommendation)

        return recommendations[:5]
