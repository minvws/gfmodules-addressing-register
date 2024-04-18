import logging

from fastapi import APIRouter, Depends

from app import container
from app.db.db import Database

logger = logging.getLogger(__name__)
router = APIRouter()

PAGE_LIMIT = 25


@router.get(
    "/examples",
    summary="Search for examples based on the query parameter",
    tags=["example_group"],
)
def get_examples(q: str, db: Database = Depends(container.get_database)) -> dict:
    """
    Returns a list of examples based on the query parameter
    """
    return {"message": "hello world"}
