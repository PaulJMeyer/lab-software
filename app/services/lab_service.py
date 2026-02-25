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