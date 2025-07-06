import os
import requests
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("NEOPLE_API_KEY")
BASE_URL = "https://api.neople.co.kr/df"

if not API_KEY:
    raise ValueError("Missing NEOPLE_API_KEY in environment variables.")


def get_json(url: str, params: dict) -> dict:
    """
    Send a GET request and return the parsed JSON response.
    Raises an error on failed request.
    """
    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        print(f"[API ERROR] Failed to fetch: {url}")
        raise e


def fetch_job_info() -> dict[str, dict]:
    """
    Fetch job and job grow (advanced class) information.
    Returns a mapping: jobId -> { jobName, rows: { jobGrowId -> jobGrowName } }
    """
    url = f"{BASE_URL}/jobs"
    data = get_json(url, {"apikey": API_KEY})

    job_list: dict[str, dict] = {}
    for job in data["rows"]:
        job_id: str = job["jobId"]
        job_name: str = job["jobName"]
        job_list[job_id] = {
            "jobName": job_name,
            "rows": {}
        }

        # Traverse each advancement to the final job grow
        for job_grow in job["rows"]:
            current = job_grow

            while current.get("next"):
                current = current["next"]

            job_grow_id = current["jobGrowId"]
            job_grow_name = current["jobGrowName"]
            job_list[job_id]["rows"][job_grow_id] = job_grow_name

    return job_list


def fetch_character_id(server_id: str, character_name: str) -> str:
    """
    Retrieve the unique character ID for a given character name on a server.
    """
    url = f"{BASE_URL}/servers/{server_id}/characters"
    data = get_json(url, {
        "apikey": API_KEY,
        "characterName": character_name
    })

    return data["rows"][0]["characterId"]


def fetch_character_status(server_id: str, character_id: str) -> dict:
    """
    Retrieve basic character status including attack speed, cast speed, etc.
    """
    url = f"{BASE_URL}/servers/{server_id}/characters/{character_id}/status"
    return get_json(url, {"apikey": API_KEY})


def fetch_character_skill_style(server_id: str, character_id: str) -> list[dict]:
    """
    Fetch the current skill style tree for the character.
    """
    url = f"{BASE_URL}/servers/{server_id}/characters/{character_id}/skill/style"
    data = get_json(url, {"apikey": API_KEY})

    return data["skill"]["style"]


def fetch_skill_list(job_id: str, job_grow_id: str) -> dict:
    """
    Fetch all skills available for a specific job + job grow ID.
    """
    url = f"{BASE_URL}/skills/{job_id}"
    return get_json(url, {
        "apikey": API_KEY,
        "jobGrowId": job_grow_id
    })


def fetch_skill_detail(job_id: str, skill_id: str) -> dict:
    """
    Fetch detailed information of a specific skill by job and skill ID.
    """
    url = f"{BASE_URL}/skills/{job_id}/{skill_id}"
    return get_json(url, {"apikey": API_KEY})
