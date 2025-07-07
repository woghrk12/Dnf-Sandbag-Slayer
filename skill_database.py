import json
import os
import neople_api

from dotenv import load_dotenv

# Global cache : { jobGrowId -> { skillId -> skillDataDict } }
skill_data: dict[str, dict[str, dict]] = {}

# Load .env for DATA_PATH
load_dotenv()
DATA_PATH = os.getenv("DATA_PATH")

if not DATA_PATH:
    raise ValueError("Missing DATA_PATH environment variable.")

if not os.path.exists(DATA_PATH):
    os.makedirs(DATA_PATH)

# Fetch and cache skill data for all jobs and job grow paths
_job_list = neople_api.fetch_job_info()

for job_id, job in _job_list.items():
    job_name = job["jobName"]
    job_grow_rows = job["rows"]
    dir_path = os.path.join(DATA_PATH, job_name)

    if not os.path.exists(dir_path):
        os.makedirs(dir_path)

    for job_grow_id, job_grow_name in job_grow_rows.items():
        file_path = os.path.join(dir_path, f"{job_grow_name}.json")

        if not os.path.exists(file_path):
            # File doesn't exist yet - fetch from API and save
            try:
                skill_list = {}
                data = neople_api.fetch_skill_list(job_id, job_grow_id)

                for skill in data["skills"]:
                    skill_id = skill["skillId"]
                    skill_name = skill["name"]
                    skill_detail = neople_api.fetch_skill_detail(job_id, skill_id)
                    level_info = skill_detail["levelInfo"]

                    skill_info = {
                        "skillName": skill_name,
                        "skillType": skill_detail["type"],
                        "optionDesc": level_info["optionDesc"],
                        "levels": {},
                        "speedCoeff": 1,
                        "speedDependency": None
                    }

                    for info in level_info["rows"]:
                        target_level = info["level"]
                        skill_info["levels"][target_level] = info["optionValue"]

                    skill_list[skill_id] = skill_info

                skill_data[job_grow_id] = skill_list

                with open(file_path, "w", encoding="utf-8") as f:
                    json.dump(skill_list, f, ensure_ascii=False, indent=2)

            except Exception as e:
                print(f"[ERROR] Failed to fetch or save skills for {job_grow_name}: {e}")
                skill_data[job_grow_id] = {}
        else:
            # File exists - Load from disk
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    skill_data[job_grow_id] = json.load(f)
            except Exception as e:
                print(f"[ERROR] Failed to load skill file for {job_grow_name}: {e}")
                skill_data[job_grow_id] = {}


def get_skill_detail(job_grow_id: str, skill_id: str) -> dict:
    """
    Return raw skill data for a given job grow and skill ID.
    """
    return skill_data[job_grow_id][skill_id]
