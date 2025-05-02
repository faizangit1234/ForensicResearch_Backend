# optimised for api endpoint
import hashlib
import random as R


def generate_dna_sequence(id: str, region: str, age: int, dna_seed: str) -> str:
    seed_hash = int(hashlib.sha256(dna_seed.encode()).hexdigest(), 16) % 10**18
    R.seed(seed_hash)

    Q = {
        "apac": ["agtc", "agct", "actg", "atgc", "actg", "agtc"],
        "na": ["gtac", "gcat", "gcta"],
        "latam": ["cgta", "ctga", "catg"],
        "emea": ["aagt", "aatg", "aagc"],
    }

    # Generate valid motifs from the seed
    motifs = [
        dna_seed[i : i + 4]
        for i in range(len(dna_seed) - 3)
        if dna_seed[i : i + 4] in {q for v in Q.values() for q in v}
    ]

    if not motifs:
        return "invalid_seed"

    # Generate sequence up to 1000 characters
    target_length = 1000
    sequence = []
    current_length = 0

    while current_length < target_length:
        motif = R.choice(motifs)
        max_repeats = (target_length - current_length) // len(motif)
        if max_repeats == 0:
            break
        repeats = R.randint(1, max_repeats)
        sequence.append(motif * repeats)
        current_length += len(motif) * repeats

    return "".join(sequence)[:target_length]


# import random as R
# import hashlib
# from functools import lru_cache
# from .file_cache import dna_cache  # Add this import
# from pathlib import Path  # Add this import

# def generate_dna_sequence(id: str, region: str, age: int, dna_seed: str):
#     # Original seed formula preserved
#     seed = f"{id}+{region}+{age}"
#     R.seed(int(hashlib.sha256(seed.encode()).hexdigest(), 16))

#     # Core optimization
#     core_value = pow(987654321, 100_000, 123456789)
#     R.seed(core_value)

#     # Get valid motifs
#     motifs = _get_valid_motifs(dna_seed, region)
#     if not motifs:
#         yield "x"
#         return

#     # Validate motif structure
#     if any(len(m) != 4 for m in motifs):
#         yield "invalid_motif"
#         return

#     yield from _build_stream(motifs)

# @lru_cache(maxsize=100)
# def _get_valid_motifs(dna_seed: str, region: str) -> list:
#     Q = {
#         "apac": ["agtc", "agct", "actg", "atgc", "actg", "agtc"],
#         "na": ["gtac", "gcat", "gcta"],
#         "latam": ["cgta", "ctga", "catg"],
#         "emea": ["aagt", "aatg", "aagc"],
#     }
#     return [
#         dna_seed[i:i+4]
#         for i in range(0, len(dna_seed)-3, 4)
#         if dna_seed[i:i+4] in Q.get(region, [])
#     ]

# def _build_stream(motifs: list):
#     L, T, C = [], 0, 1010101010
#     chunk_size = 65536  # 64KB chunks optimized

#     while T < C:
#         Z = R.choice(motifs)
#         max_repeats = (C - T) // len(Z)

#         if max_repeats == 0:
#             break

#         # Critical fix: safe randomization
#         upper_bound = min(100000, max_repeats)
#         lower_bound = max(1, min(1000, upper_bound))
#         repeats = R.randint(lower_bound, upper_bound)

#         chunk = Z * repeats
#         L.append(chunk)
#         T += len(chunk)

#         # Memory-safe chunk handling
#         while sum(len(s) for s in L) >= chunk_size:
#             buffered = "".join(L)
#             yield buffered[:chunk_size]
#             L = [buffered[chunk_size:]]

#     if L:
#         final_chunk = "".join(L)[:C-T]
#         yield final_chunk

# def generate_to_file(id: str, region: str, age: int, dna_seed: str) -> str:
#     """Generate sequence and save to file"""
#     params_hash = hashlib.sha256(f"{id}{region}{age}{dna_seed}".encode()).hexdigest()
#     file_path = dna_cache.get_file_path(params_hash)

#     if not Path(file_path).exists():
#         with open(file_path, 'w') as f:
#             for chunk in generate_dna_sequence(id, region, age, dna_seed):
#                 f.write(chunk)

#     return file_path
