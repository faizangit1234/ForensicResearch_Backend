import logging

from fastapi import APIRouter, HTTPException

from app.models.dna import CompareRequest
from app.services.dna_generator import generate_dna_sequence
from app.services.similarity import compare_dna_sequences
from app.utils.file_handler import get_record_by_id

router = APIRouter()
logger = logging.getLogger(__name__)


@router.post("/compare-sequences/")
def compare_sequences(payload: CompareRequest):
    try:
        # Existing record validation
        record1 = get_record_by_id(payload.id1)
        record2 = get_record_by_id(payload.id2)
        if not record1 or not record2:
            logger.warning(f"Missing records: {payload.id1} and/or {payload.id2}")
            raise HTTPException(status_code=404, detail="One or both IDs not found")

        # Sequence generation with validation
        seq1 = "".join(
            generate_dna_sequence(
                record1["id"], record1["region"], int(record1["age"]), record1["seed"]
            )
        )

        seq2 = "".join(
            generate_dna_sequence(
                record2["id"], record2["region"], int(record2["age"]), record2["seed"]
            )
        )

        # hybrid comparison
        similarity = compare_dna_sequences(seq1, seq2)

        logger.info(f"Comparison completed: {payload.id1} vs {payload.id2}")
        return {
            "similarity_score": similarity,
            "comparison_method": "hybrid_jaccard_nw",
        }

    except HTTPException as he:
        raise he
    except Exception as e:
        logger.error(f"Comparison failed: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error")
