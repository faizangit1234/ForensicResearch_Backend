import numpy as np


def needleman_wunsch(seq1: str, seq2: str, match=2, mismatch=-1, gap=-1) -> float:
    """Optimized Needleman-Wunsch with numpy"""
    n, m = len(seq1), len(seq2)

    # Matrix initialization using numpy for speed
    matrix = np.zeros((n + 1, m + 1))
    matrix[:, 0] = np.arange(0, (n + 1) * gap, gap)
    matrix[0, :] = np.arange(0, (m + 1) * gap, gap)

    # Matrix filling with vectorized operations
    for i in range(1, n + 1):
        for j in range(1, m + 1):
            diag = matrix[i - 1, j - 1] + (
                match if seq1[i - 1] == seq2[j - 1] else mismatch
            )
            up = matrix[i - 1, j] + gap
            left = matrix[i, j - 1] + gap
            matrix[i, j] = max(diag, up, left)

    # Normalize score to 0-1 range
    max_score = min(n, m) * match
    return max(0.0, matrix[n, m] / max_score)
