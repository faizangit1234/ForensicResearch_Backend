import hashlib
import os
from pathlib import Path

from diskcache import Cache


class DNACache:
    def __init__(self):
        self.cache = Cache("cache/dna_files")
        self.storage_path = Path("dna_sequences")
        self.storage_path.mkdir(exist_ok=True)

    def get_file_path(self, params_hash: str) -> str:
        """Get cached file path or generate new"""
        if file_path := self.cache.get(params_hash):
            return file_path

        file_path = self.storage_path / f"{params_hash}.txt"
        self.cache.set(params_hash, str(file_path), expire=86400)
        return str(file_path)

    def delete_expired(self):
        """Daily cleanup task"""
        for expired_key in self.cache.expire():
            file_path = Path(self.cache.pop(expired_key))
            if file_path.exists():
                file_path.unlink()


dna_cache = DNACache()
