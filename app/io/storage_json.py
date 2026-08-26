import json
from pathlib import Path
from app.domain.models import Sample


def save_samples(path: Path, samples_dict):

    path.parent.mkdir(parents=True, exist_ok=True)

    data = [sample.model_dump() for sample in samples_dict.values()]

    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)


def load_samples(path: Path):

    if not path.exists():
        return {}

    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)

    samples_dict = {}

    for item in data:

        sample = Sample.model_validate(item)

        if sample.sample_id in samples_dict:
            raise ValueError(f"Duplicate ID in file: {sample.sample_id}")

        samples_dict[sample.sample_id] = sample

    return samples_dict
