class Sample:
    def __init__(self, sample_id: str, sample_dna: str):
        self.sample_id = sample_id
        self.sample_dna = sample_dna        
        pass
    def __repr__(self):
        return str((self.sample_id, len(self.sample_dna)))
        pass

# from pydantic import BaseModel

# class SamplePydantic(BaseModel):
#     sample_id: str
#     sample_dna: str

#crud pattern