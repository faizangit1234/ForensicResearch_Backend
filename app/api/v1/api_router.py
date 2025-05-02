from fastapi import APIRouter

from app.api.v1.endpoints import ask, compare, generate, upload

router = APIRouter()

router.include_router(upload.router, prefix="", tags=["Upload"])
router.include_router(generate.router, prefix="", tags=["Generate"])
router.include_router(compare.router, prefix="", tags=["Compare"])
router.include_router(ask.router, prefix="", tags=["Ask"])
