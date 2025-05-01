# ALSO WORKING 2ND OPTION
import logging

from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse

from app.services.dna_generator import generate_dna_sequence
from app.utils.file_handler import get_record_by_id

# Initialize logger
logger = logging.getLogger(__name__)

router = APIRouter()


@router.get(
    "/generate-sequence2/{sample_id}",
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
