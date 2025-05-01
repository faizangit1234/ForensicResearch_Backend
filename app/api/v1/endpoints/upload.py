import logging
import os
import uuid

from fastapi import APIRouter, File, HTTPException, UploadFile
from pandas import DataFrame

from app.utils.file_handler import read_csv, save_uploaded_file

router = APIRouter()
logger = logging.getLogger(__name__)


@router.post("/upload-csv/")
async def upload_csv(file: UploadFile = File(...)):
    try:
        # Generate unique filename with original extension
        file_id = str(uuid.uuid4())
        original_ext = os.path.splitext(file.filename)[1]
        file_path = f"app/storage/uploads/{file_id}{original_ext}"

        if file.content_type not in ["text/csv", "application/vnd.ms-excel"]:
            raise HTTPException(400, "Only CSV files are allowed")

        # Save with size limit (5MB)
        await save_uploaded_file(file, file_path, max_size=5 * 1024 * 1024)

        # Read CSV with improved validation
        df = read_csv(file_path)

        # Additional validation
        if df.duplicated("id").any():
            duplicates = df[df.duplicated("id")]["id"].tolist()
            raise HTTPException(400, f"Duplicate IDs found: {duplicates[:5]}")

        # Validate numerical ranges ,, commented for future validation
        # if (df['age'] < 0).any():
        #     raise HTTPException(400, "Age cannot be negative")

        # Validate CSV structure
        required_columns = ["id", "region", "age", "seed"]
        if not all(col in df.columns for col in required_columns):
            missing = set(required_columns) - set(df.columns)
            raise HTTPException(400, f"Missing columns: {', '.join(missing)}")

        # Validate age values
        invalid_ages = []
        for index, row in df.iterrows():
            try:
                age = int(row["age"])
                if age < 0:
                    invalid_ages.append((index, row["age"], "Negative value"))
            except ValueError:
                invalid_ages.append((index, row["age"], "Not an integer"))
            except KeyError:
                raise HTTPException(400, "CSV file is missing 'age' column")

        if invalid_ages:
            error_details = [
                f"Row {idx+2}: Value '{val}' - {reason}"  # +2 for 0-index and header row
                for idx, val, reason in invalid_ages[:5]  # Show first 5 errors
            ]
            error_message = "Invalid age values:\n" + "\n".join(error_details)
            if len(invalid_ages) > 5:
                error_message += f"\n...and {len(invalid_ages)-5} more errors"
            raise HTTPException(400, error_message)

        # Region validation
        valid_regions = ["apac", "na", "latam", "emea"]
        invalid_regions = df[~df["region"].str.lower().isin(valid_regions)]
        if not invalid_regions.empty:
            raise HTTPException(
                400, f"Invalid regions: {invalid_regions['region'].unique().tolist()}"
            )

        # Seed validation
        short_seeds = df[df["seed"].str.len() < 4]
        if not short_seeds.empty:
            raise HTTPException(
                400, f"Short seeds in rows: {short_seeds.index.tolist()}"
            )

        # Store data (replace with database logic)
        processed_path = f"app/storage/processed/{file_id}.parquet"
        df.to_parquet(processed_path)

        return {"message": f"Processed {len(df)} records", "file_id": file_id}

    except HTTPException as he:
        logger.warning(f"Validation error: {he.detail}")
        raise
    except Exception as e:
        logger.error(f"Upload failed: {str(e)}", exc_info=True)
        # Cleanup failed upload
        if "file_path" in locals() and os.path.exists(file_path):
            os.remove(file_path)
        raise HTTPException(500, "File processing error")
    finally:
        # Cleanup temporary files
        if "file" in locals():
            await file.close()
