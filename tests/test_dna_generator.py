import random as R

from app.services.dna_generator import generate_dna_sequence


def original_generation_function(id: int, region: str, age: int, dna_seed: str) -> str:
    # ... [paste the original slow implementation here] ...

def test_sequence_consistency():
    test_params = (1, "apac", 50, "agtc"*100)
    
    # Original implementation
    R.seed(f"{test_params[0]}+{test_params[1]}+{test_params[2]}")
    original = original_generation_function(*test_params)
    
    # Optimized implementation
    optimized = generate_dna_sequence(*test_params)
    
    # Check first 1000 characters match
    assert original[:1000] == optimized[:1000], "First 1000 characters mismatch"
    
    # Check total length matches
    assert len(original) == len(optimized), "Length mismatch"
    
    print("Consistency test passed!")

if __name__ == "__main__":
    test_sequence_consistency()