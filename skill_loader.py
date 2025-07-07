from dataclasses import dataclass
from typing import Optional
from skill_database import get_skill_detail


@dataclass
class SkillLevelInfo:
    values: dict[str, float]


@dataclass
class SkillData:
    skill_id: str
    name: str
    skill_type: str  # "active", "passive"
    description: str
    levels: dict[int, SkillLevelInfo]
    speed_coeff: float = 1.0
    speed_dependency: Optional[str] = None  # "attack", "cast", or None


def load_skill(job_grow_id: str, skill_id: str) -> SkillData:
    """
    Load a structured SkillData object from the raw skill JSON data
    """
    raw = get_skill_detail(job_grow_id, skill_id)

    # Parse Level info
    levels = {int(level): SkillLevelInfo(level_data) for level, level_data in raw["levels"].items()}

    return SkillData(
        skill_id=skill_id,
        name=raw["skillName"],
        skill_type=raw["skillType"],
        description=raw["optionDesc"],
        levels=levels,
        speed_coeff=raw.get("speedCoeff", 1),
        speed_dependency=raw.get("speedDependency", None)
    )
