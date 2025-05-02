# Using Pydantic for data validation and serialization of request/response models
from pydantic import BaseModel, Field


# Response schema for returning a DNA sample’s metadata and sequence
class DNASequenceResponse(BaseModel):
    sample_id: str
    region: str
    age: int
    dna_sequence: str
    cached: bool

    class Config:
        json_schema_extra = {
            "example": {
                "sample_id": "id_0001",
                "region": "apac",
                "age": 35,
                "dna_sequence": "AGTCGTAAGTC...",
                "cached": False,
            }
        }


class CompareRequest(BaseModel):
    id1: str
    id2: str


class AskRequest(BaseModel):
    question: str = Field(
        ...,
        min_length=20,
        max_length=1000,
        example="How to differentiate degradation from inhibition in PCR?",
        description="Forensic DNA analysis question requiring expert evaluation",
    )
