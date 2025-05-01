import pytest
from app.services.dna_generator import generate_dna_sequence

def test_sequence_consistency():
    """
    Given the same seed and parameters, generate_dna_sequence
    should return identical sequences every time and length == 1000.
    """
    seed = "agtc"  # a valid motif part of Q['apac']
    seq1 = generate_dna_sequence(id="id_0001", region="apac", age=30, dna_seed=seed)
    seq2 = generate_dna_sequence(id="id_0001", region="apac", age=30, dna_seed=seed)

    # They must be the same (deterministic given the seed)
    assert seq1 == seq2
    # And should be exactly 1000 characters long
    assert isinstance(seq1, str) and len(seq1) == 1000

def test_invalid_seed_returns_invalid_seed():
    """
    If the seed contains no valid motifs, the function should return "invalid_seed".
    """
    bad_seed = "xxxx"  # not in any Q motifs
    result = generate_dna_sequence(id="id_0002", region="na", age=25, dna_seed=bad_seed)
    assert result == "invalid_seed"
