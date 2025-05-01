import csv
from datetime import datetime
from pathlib import Path


class SequenceRecorder:
    def __init__(self):
        self.file_path = Path("sequence_logs.csv")
        self._init_csv()

    def _init_csv(self):
        if not self.file_path.exists():
            with open(self.file_path, "w") as f:
                writer = csv.writer(f)
                writer.writerow(
                    [
                        "timestamp",
                        "sample_id",
                        "file_size_mb",
                        "compression_ratio",
                        "checksum",
                    ]
                )

    def log_download(self, sample_id: str, file_path: str):
        file = Path(file_path)
        stats = {
            "size": file.stat().st_size,
            "checksum": hashlib.md5(file.read_bytes()).hexdigest(),
        }

        with open(self.file_path, "a") as f:
            writer = csv.writer(f)
            writer.writerow(
                [
                    datetime.utcnow().isoformat(),
                    sample_id,
                    round(stats["size"] / (1024 * 1024), 2),
                    0.3,  # Example compression ratio
                    stats["checksum"],
                ]
            )


recorder = SequenceRecorder()
