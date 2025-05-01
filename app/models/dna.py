# Using Pydantic for data validation and serialization of request/response models
from pydantic import BaseModel


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
    # User’s natural-language query text
    question: str
