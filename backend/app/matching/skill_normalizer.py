import json
import os
import logging
from typing import Dict, List, Tuple

logger = logging.getLogger(__name__)


class SkillNormalizer:
    _aliases: Dict[str, str] = {}
    _strict_inequivalent: List[Tuple[str, str]] = []

    @classmethod
    def load_aliases(cls, data_path: str = "data/skill_aliases.json"):
        possible_paths = [
            data_path,
            os.path.join(os.path.dirname(__file__), "../../../data/skill_aliases.json"),
            os.path.join(os.getcwd(), "data/skill_aliases.json")
        ]

        for path in possible_paths:
            if os.path.exists(path):
                try:
                    with open(path, "r", encoding="utf-8") as f:
                        data = json.load(f)
                        cls._aliases = data.get("aliases", {})
                        cls._strict_inequivalent = [tuple(pair) for pair in data.get("strict_inequivalent", [])]
                    logger.info(f"Loaded {len(cls._aliases)} skill aliases from {path}")
                    return
                except Exception as e:
                    logger.warning(f"Error loading skill aliases from {path}: {e}")

        cls._aliases = {
            "Spring": "Spring Framework",
            "Spring Boot": "Spring Boot",
            "Amazon Web Services": "AWS",
            "AWS EC2": "AWS",
            "AWS S3": "AWS",
            "Postgres": "PostgreSQL",
            "Postgresql": "PostgreSQL",
            "JS": "JavaScript",
            "TS": "TypeScript",
            "Node": "Node.js",
            "Nodejs": "Node.js",
            "K8s": "Kubernetes",
            "Web Services": "REST API",
            "RESTful API": "REST API"
        }
        cls._strict_inequivalent = [
            ("MySQL", "PostgreSQL"),
            ("Java", "JavaScript"),
            ("AWS", "Azure"),
            ("AWS", "GCP"),
            ("React", "React Native")
        ]

    @classmethod
    def normalize(cls, skill_name: str) -> str:
        if not cls._aliases:
            cls.load_aliases()

        cleaned = skill_name.strip()
        for alias, canonical in cls._aliases.items():
            if cleaned.lower() == alias.lower():
                return canonical

        return cleaned

    @classmethod
    def are_strictly_inequivalent(cls, skill_a: str, skill_b: str) -> bool:
        if not cls._aliases:
            cls.load_aliases()

        norm_a = cls.normalize(skill_a).lower()
        norm_b = cls.normalize(skill_b).lower()

        for item_a, item_b in cls._strict_inequivalent:
            if (norm_a == item_a.lower() and norm_b == item_b.lower()) or (norm_a == item_b.lower() and norm_b == item_a.lower()):
                return True

        return False
