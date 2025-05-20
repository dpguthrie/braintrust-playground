"""Currently, using the is_valid_python scorer from the tools.py file.

This is an alternative approach to using the Pythonium API.
"""

import pydantic
import requests


class PythonCode(pydantic.BaseModel):
    output: str


def is_valid_python(output: str) -> int:
    url = "https://pythonium.net/checker"
    headers = {
        "accept": "*/*",
        "accept-language": "en-US,en;q=0.9",
        "content-type": "application/x-www-form-urlencoded",
        "dnt": "1",
        "origin": "https://pythonium.net",
        "priority": "u=1, i",
        "referer": "https://pythonium.net/linter",
        "sec-ch-ua": '"Not.A/Brand";v="99", "Chromium";v="136"',
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": '"macOS"',
        "sec-fetch-dest": "empty",
        "sec-fetch-mode": "cors",
        "sec-fetch-site": "same-origin",
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36",
    }
    response = requests.post(url, data=output, headers=headers)
    try:
        data = response.json()
    except ValueError:
        return None

    error_code: int = data["error"]
    is_valid: bool = error_code == 0
    return int(is_valid)
