import os
import tempfile

from diskcache import FanoutCache


class SequenceCache:
    def __init__(self):
        self.cache = FanoutCache(
            "cache/dna_sequences", size_limit=10**10, disk_pickle_protocol=4  # 10GB
        )

    def get(self, key):
        return self.cache.get(key)

    def set(self, key, file_path):
        self.cache.set(key, file_path, expire=86400)

    def stream(self, key):
        file_path = self.get(key)
        if file_path and os.path.exists(file_path):
            with open(file_path, "r") as f:
                while chunk := f.read(65536):  # 64KB chunks
                    yield chunk


cache = SequenceCache()
