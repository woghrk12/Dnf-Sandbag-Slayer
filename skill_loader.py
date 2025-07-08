from dataclasses import dataclass, field
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


@dataclass
class SkillMeta:
    skill_id: str
    cooldown: float
    base_cast_time: float  # Base cast time before speed scaling
    delay_after: float  # Post-cast delay
    is_install: bool = False  # Whether this skill is an install-type skill
    speed_dependency: Optional[str] = None  # "attack", "cast", or None
    speed_coeff: float = 1.0  # Multiplier for base cast time
    cancel_rules: list[str] = field(default_factory=list)  # Skills whose after-delay this skill can cancel
    merge_rules: list[str] = field(default_factory=list)  # Skills this can merge with mid-cast


@dataclass
class FullSkill:
    data: SkillData
    meta: SkillMeta

    def get_cast_time(self, stats: CharacterStats) -> float:
        """
        Calculate the actual cast time of the skill based on the character's stats.
        """
        if self.meta.speed_dependency == "attack":
            speed = 1 + stats.attack_speed / 100
        elif self.meta .speed_dependency == "cast":
            speed = 1 + stats.cast_speed / 100
        else:
            speed = 1.0

        return self.meta.base_cast_time + self.meta.speed_coeff / speed
