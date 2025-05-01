import logging
import os

import pandas as pd
from fastapi import HTTPException, UploadFile

from app.core.config import DATA_FILE_PATH

logger = logging.getLogger(__name__)


async def save_uploaded_file(
    file: UploadFile, file_path: str, max_size: int = 5 * 1024 * 1024
):
    """Save uploaded file with size validation"""
    try:
        # Create directory if needed
        os.makedirs(os.path.dirname(file_path), exist_ok=True)

        # Save file in chunks with size validation
        total_size = 0
        with open(file_path, "wb") as buffer:
            while True:
                chunk = await file.read(1024 * 1024)  # 1MB chunks
                if not chunk:
                    break
                total_size += len(chunk)
                if total_size > max_size:
                    os.remove(file_path)
                    raise HTTPException(
                        413, f"File exceeds {max_size//1024//1024}MB limit"
                    )
                buffer.write(chunk)

        logger.info(f"Saved file: {file_path} ({total_size} bytes)")
        return True

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"File save failed: {str(e)}")
        if os.path.exists(file_path):
            os.remove(file_path)
        raise HTTPException(500, "File upload failed")


logger = logging.getLogger(__name__)


def read_csv(file_path: str) -> pd.DataFrame:
    """Read and validate CSV file structure"""
    try:
        # Read CSV with basic validation
        df = pd.read_csv(
            file_path,
            dtype={"id": str, "region": str, "seed": str},
            converters={"age": lambda x: str(x).strip()},
            na_values=["", "NA", "N/A", "null", "NaN"],
            keep_default_na=False,
        )

        # Check for required columns
        required_columns = ["id", "region", "age", "seed"]
        missing_cols = [col for col in required_columns if col not in df.columns]
        if missing_cols:
            raise HTTPException(400, f"Missing required columns: {missing_cols}")

        return df

    except KeyError as e:
        raise HTTPException(400, f"Missing required column: {str(e)}")
    except pd.errors.ParserError:
        raise HTTPException(400, "Invalid CSV file structure")


def get_record_by_id(sample_id: str):
    try:
        df = read_csv(DATA_FILE_PATH)
        df["id"] = df["id"].astype(str)

        # Find matching record
        match = df[df["id"] == sample_id]
        if match.empty:
            return None

        record = match.iloc[0].to_dict()

        # Validate critical fields
        validation_errors = []

        if not str(record.get("age", "")).strip():
            validation_errors.append("Missing age value")

        seed = str(record.get("seed", ""))
        if len(seed) < 4:
            validation_errors.append("Seed must be at least 4 characters")

        if validation_errors:
            error_msg = f"Invalid record for {sample_id}: " + ", ".join(
                validation_errors
            )
            logger.error(error_msg)
            raise HTTPException(status_code=400, detail=error_msg)

        return record

    except HTTPException as he:
        # Re-raise validation errors
        raise he

    except Exception as e:
        logger.error(f"Database error: {str(e)}")
        raise HTTPException(status_code=500, detail="Data storage system error")


# another approach ,also working

# import pandas as pd
# from app.core.config import DATA_FILE_PATH

# def save_uploaded_file(contents: bytes):
#     with open(DATA_FILE_PATH, 'wb') as f:
#         f.write(contents)

# def read_csv():
#     return pd.read_csv(DATA_FILE_PATH)

# # def get_record_by_id(sample_id: str):
# #     df = read_csv()
# #     # Handle numeric IDs and string IDs uniformly
# #     match = df[df["id"].astype(str) == str(sample_id)]
# #     if not match.empty:
# #         record = match.iloc[0]
# #         # Check for missing critical fields
# #         if pd.isnull(record['age']) or pd.isnull(record['seed']):
# #             return None
# #         return record.to_dict()
# #     return None

# def get_record_by_id(sample_id: str):
#     df = read_csv()

#     # Convert all IDs to strings for consistent comparison
#     df["id"] = df["id"].astype(str)

#     match = df[df["id"] == sample_id]

#     if not match.empty:
#         record = match.iloc[0]
#         # Additional validation
#         if pd.isnull(record['seed']) or len(str(record['seed'])) < 4:
#             logger.error(f"Invalid seed for ID {sample_id}")
#             return None
#         return record.to_dict()
#     return None
