import logging

# Configure logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

handler = logging.FileHandler("dna_api_errors.log")
formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
handler.setFormatter(formatter)
logger.addHandler(handler)

import hashlib

from diskcache import Cache
from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse

from app.models.dna import DNASequenceResponse  # Add this import
from app.services.dna_generator import generate_dna_sequence
from app.utils.file_handler import get_record_by_id

router = APIRouter()

# Create cache with 24-hour expiration
cache = Cache(
    "cache/dna_sequences", disk_pickle_protocol=4, timeout=86400  # 24 hours in seconds
)


def make_cache_key(record: dict) -> str:
    """Create a unique hash key from the record."""
    key_str = f"{record['id']}_{record['region']}_{record['age']}_{record['seed']}"
    return hashlib.sha256(key_str.encode()).hexdigest()


@router.get(
    "/generate-sequence/{sample_id}",
    response_model=DNASequenceResponse,
    responses={
        200: {"description": "Successfully generated DNA sequence"},
        400: {"description": "Invalid record data"},
        404: {"description": "Sample ID not found"},
        500: {"description": "Internal server error"},
    },
    operation_id="generate_sequence",
)
def generate_sequence(sample_id: str):
    """
    Generate DNA sequence for a given sample ID with proper error handling
    """
    try:
        # Attempt to retrieve the record
        record = get_record_by_id(sample_id)

        if not record:
            raise HTTPException(
                status_code=404, detail=f"Sample ID {sample_id} not found in database"
            )

        # Generate the cache key
        cache_key = make_cache_key(record)

        # Check if the result is already cached
        if cache_key in cache:
            return {
                "dna_sequence": cache[cache_key],
                "sample_id": record["id"],
                "region": record["region"],
                "age": record["age"],
                "cached": True,  # Indicate that the result was cached
            }

        # If not cached, generate the sequence
        sequence = generate_dna_sequence(
            id=record["id"],
            region=record["region"],
            age=record["age"],
            dna_seed=record["seed"],
        )

        # Save the generated sequence to cache
        cache[cache_key] = sequence

        return {
            "dna_sequence": sequence,
            "sample_id": record["id"],
            "region": record["region"],
            "age": record["age"],
            "cached": False,  # Indicate that the result was not cached
        }

    except HTTPException as he:
        # Re-raise documented HTTP exceptions
        raise he

    except Exception as e:
        logger.error(f"Unexpected error processing {sample_id}: {str(e)}")
        raise HTTPException(
            status_code=500, detail="Internal server error - please contact support"
        )


@router.get(
    "/generate-sequence-stream/{sample_id}",
    operation_id="generate_sequence_stream",
    response_class=StreamingResponse,
    responses={
        200: {
            "content": {"text/plain": {}},
            "description": "Streaming DNA sequence",
        },
        404: {"description": "Sample not found"},
        500: {"description": "Internal server error"},
    },
)
async def generate_sequence(sample_id: str):
    try:
        record = get_record_by_id(sample_id)
        if not record:
            raise HTTPException(status_code=404, detail="Sample ID not found")

        return StreamingResponse(
            generate_dna_sequence(
                id=record["id"],
                region=record["region"],
                age=int(record["age"]),
                dna_seed=record["seed"],
            ),
            media_type="text/plain",
            headers={
                "Content-Disposition": f"inline; filename={sample_id}_dna.txt",
                "X-Content-Type-Options": "nosniff",
            },
        )

    except HTTPException as he:
        raise he
    except Exception as e:
        logger.error(f"Generation error: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error")
