from fastapi import APIRouter
from pydantic import BaseModel

from services.github_service import search_github_repositories

router = APIRouter()


class SearchRequest(BaseModel):
    query: str
    languages: list[str]


@router.get("/")
def root():
    return {"message": "Zafirus Challenge API running"}


@router.post("/search")
def search_repositories(data: SearchRequest):

    results = search_github_repositories(
        data.query,
        data.languages
    )

    return results