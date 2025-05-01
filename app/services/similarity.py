# code with new algorithm of comparison
from app.services.alignment import needleman_wunsch


def extract_motifs(sequence: str, motif_length: int = 4) -> set:
    return {
        sequence[i : i + motif_length] for i in range(len(sequence) - motif_length + 1)
    }


def jaccard_similarity(seq1: str, seq2: str) -> float:
    """Existing Jaccard method as fallback"""
    motifs1 = extract_motifs(seq1)
    motifs2 = extract_motifs(seq2)
    intersection = motifs1.intersection(motifs2)
    union = motifs1.union(motifs2)
    return len(intersection) / len(union) if union else 0.0


def compare_dna_sequences(seq1: str, seq2: str, threshold: float = 0.5) -> float:
    """Hybrid comparison approach"""
    if not seq1 or not seq2:
        return 0.0
    # First check Jaccard similarity
    jaccard = jaccard_similarity(seq1, seq2)

    # Only use Needleman-Wunsch for promising matches
    if jaccard < threshold:
        return round(jaccard, 4)

    # For high similarity candidates, perform detailed alignment
    alignment_score = needleman_wunsch(
        seq1[:1000] if len(seq1) >= 1000 else seq1,
        seq2[:1000] if len(seq2) >= 1000 else seq2,
    )
    # Use first 1000 characters for practical computation
    alignment_score = needleman_wunsch(seq1[:1000], seq2[:1000])

    # Combine scores with weighted average
    combined_score = 0.7 * alignment_score + 0.3 * jaccard
    return round(combined_score, 4)


# using another approach


# def extract_motifs(sequence: str, motif_length: int = 4) -> set:
#     return {sequence[i:i+motif_length] for i in range(len(sequence) - motif_length + 1)}

# def compare_dna_sequences(seq1: str, seq2: str) -> float:
#     motifs1 = extract_motifs(seq1)
#     motifs2 = extract_motifs(seq2)

#     intersection = motifs1.intersection(motifs2)
#     union = motifs1.union(motifs2)

#     if not union:
#         return 0.0
#     return round(len(intersection) / len(union), 4)
