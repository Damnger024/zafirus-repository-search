from models.repository import Repository
from scoring.scorer import calculate_score
from utils.explanation import generate_explanation
from filters.repo_filters import filter_repositories
from requests.exceptions import RequestException
from fastapi import HTTPException

from services.query_builder import build_query

import os
import requests

from dotenv import load_dotenv

load_dotenv()

GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")


def search_github_repositories(query, languages):

    search_query = build_query(query, languages)

    url = "https://api.github.com/search/repositories"

    headers = {
        "Authorization": f"Bearer {GITHUB_TOKEN}",
        "Accept": "application/vnd.github.mercy-preview+json"
    }

    params = {
        "q": search_query,
        "sort": "stars",
        "order": "desc",
        "per_page": 75
    }

    try:

        print(search_query)
        response = requests.get(
            url,
            headers=headers,
            params=params,
            timeout=10
        )

    except RequestException:

        raise HTTPException(
            status_code=503,
            detail="Unable to connect to GitHub API"
        )

    if response.status_code == 403:

        remaining = response.headers.get("X-RateLimit-Remaining")
        reset_time = response.headers.get("X-RateLimit-Reset")

        if remaining == "0":

            return {
                "repositories": [],
                "message": "GitHub API rate limit exceeded. Please try again later.",
                "rate_limit": {
                    "remaining": remaining,
                    "reset_at": reset_time
                }
            }

        raise HTTPException(
            status_code=403,
            detail="Access forbidden by GitHub API"
        )

    if response.status_code == 401:
        raise HTTPException(
            status_code=500,
            detail="Invalid GitHub token"
        )

    if response.status_code != 200:
        raise HTTPException(
            status_code=response.status_code,
            detail=response.text
        )

    try:
        data = response.json()

    except Exception:
        raise HTTPException(
            status_code=500,
            detail="Invalid GitHub API response"
        )

    repositories = []

    for repo in data.get("items", []):

        repo_data = Repository(
            name=repo["name"],
            full_name=repo["full_name"],
            description=repo.get("description"),
            stars=repo["stargazers_count"],
            language=repo.get("language"),
            last_update=repo["updated_at"],
            url=repo["html_url"],
            fork=repo["fork"],
            archived=repo["archived"],
            topics=repo.get("topics", []),
            homepage=repo.get("homepage")
        )

        score_data = calculate_score(
            repo_data,
            query
        )

        repo_data.score = score_data["total_score"]

        repo_data.confidence = score_data["confidence"]

        repo_data.score_breakdown = score_data["breakdown"]

        repo_data.signals = score_data["signals"]

        repo_data.reasons = generate_explanation(
            repo_data,
            query
        )

        repositories.append(repo_data)

    repositories = filter_repositories(repositories)

    if not data.get("items"):
        return {
            "repositories": [],
            "message": "No repositories found on GitHub for this query."
        }

    if not repositories:
        return {
            "repositories": [],
            "message": "No relevant repositories found. Try a broader query."
        }

    repositories.sort(
        key=lambda x: (
            x.score,
            x.signals.get("full_match", False),
            x.stars,
            x.signals.get("very_recent_activity", False)
        ),
        reverse=True
    )

    top_repositories = repositories[:5]

    insight = None

    if len(top_repositories) >= 2:

        top1 = top_repositories[0]
        top2 = top_repositories[1]

        if top1.score > top2.score:

            if top1.stars < top2.stars:
                insight = (
                    f"{top1.name} ranks higher than {top2.name} despite fewer stars "
                    f"due to better activity or relevance."
                )

            elif top1.signals.get("very_recent_activity") and not top2.signals.get("very_recent_activity"):
                insight = (
                    f"{top1.name} ranks higher due to more recent activity."
                )

            elif top1.signals.get("full_match") and not top2.signals.get("full_match"):
                insight = (
                    f"{top1.name} ranks higher due to better match with the search query."
                )

            else:
                insight = (
                    f"{top1.name} slightly outperforms {top2.name} based on combined scoring factors."
                )

    for i, repo in enumerate(top_repositories):
        repo.rank = i + 1

    return {
        "repositories": top_repositories,
        "insight": insight
    }