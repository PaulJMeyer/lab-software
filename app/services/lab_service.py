from app.domain.models import Sample


class LabService:
    def __init__(self):
        # sample_id -> Sample
        self._samples = {}

    def add_sample(self, sample: Sample):
        if sample.sample_id in self._samples:
            raise ValueError(f"Sample ID already exists: {sample.sample_id}")

        self._samples[sample.sample_id] = sample

    def list_samples(self):
        return list(self._samples.values())

    def get_state(self):
        return self._samples

    def set_state(self, samples_dict):
        self._samples = samples_dict

    def delete_sample(self, sample_id: str):
        if sample_id not in self._samples:
            raise ValueError(f"Sample ID nicht gefunden: {sample_id}")
        del self._samples[sample_id]

    def find_sample(self, sample_id: str):
        return self._samples.get(sample_id, None)