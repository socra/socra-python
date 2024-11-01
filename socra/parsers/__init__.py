import json


def parse_json(json_str: str) -> dict:
    # if begins with ```, strip first line
    if json_str.startswith("```"):
        json_str = json_str.split("\n", 1)[1]

    # if ends with ```, strip last line
    if json_str.endswith("```"):
        json_str = json_str.rsplit("\n", 1)[0]
    return json.loads(json_str)
