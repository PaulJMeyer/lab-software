import json
from pathlib import Path
from app.domain.models import FragmentTemplate


def save_templates(path: Path, templates_dict):

    path.parent.mkdir(parents=True, exist_ok=True)

    data = [template.model_dump() for template in templates_dict.values()]

    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)


def load_templates(path: Path):

    if not path.exists():
        return {}

    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)

    templates_dict = {}

    for item in data:

        template = FragmentTemplate.model_validate(item)

        if template.name in templates_dict:
            raise ValueError(f"Duplicate template name in file: {template.name}")

        templates_dict[template.name] = template

    return templates_dict
