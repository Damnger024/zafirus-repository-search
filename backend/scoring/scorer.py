from scoring.weights import *
from utils.helpers import calculate_days_inactive
from utils.helpers import tokenize_text


LOW_QUALITY_TERMS = {
    "awesome",
    "example",
    "examples",
    "demo",
    "tutorial",
    "boilerplate",
    "template",
    "starter"
}


def calculate_score(repo, query):

    score = 0

    breakdown = {
        "stars": 0,
        "relevance": 0,
        "documentation": 0,
        "activity": 0,
        "penalties": 0
    }

    signals = {
        "elite_popularity": False,
        "high_popularity": False,
        "medium_popularity": False,

        "very_recent_activity": False,
        "recent_activity": False,
        "moderate_activity": False,
        "low_activity": False,

        "full_match": False,
        "partial_match": False,

        "good_documentation": False,

        "archived": False,

        "relevant_fork": False,
        "irrelevant_fork": False
    }

    # --- STARS ---
    stars = repo.stars

    if stars >= 50000:

        score += STARS_ELITE
        breakdown["stars"] += STARS_ELITE

        signals["elite_popularity"] = True

    elif stars >= 10000:

        score += STARS_HIGH
        breakdown["stars"] += STARS_HIGH

        signals["high_popularity"] = True

    elif stars >= 3000:

        score += STARS_MEDIUM
        breakdown["stars"] += STARS_MEDIUM

        signals["medium_popularity"] = True

    elif stars >= 500:

        score += STARS_LOW
        breakdown["stars"] += STARS_LOW

    else:

        score += STARS_MINIMAL
        breakdown["stars"] += STARS_MINIMAL

    # --- RELEVANCIA ---

    query_tokens = tokenize_text(query)

    name_tokens = tokenize_text(repo.name or "")
    description_tokens = tokenize_text(repo.description or "")
    topic_tokens = tokenize_text(" ".join(repo.topics))

    relevance_score = 0

    for token in query_tokens:

        if len(token) < 3:
            continue

        if token in name_tokens:
            relevance_score += 12

        if token in topic_tokens:
            relevance_score += 8

        if token in description_tokens:
            relevance_score += 5
    
    relevance_score = min(relevance_score, RELEVANCE_FULL_MATCH)

    score += relevance_score
    breakdown["relevance"] += relevance_score

    if relevance_score >= 20:
        signals["full_match"] = True

    elif relevance_score > 0:
        signals["partial_match"] = True

    # --- DOCUMENTATION ---

    documentation_score = 0

    if repo.description and len(repo.description.strip()) >= 20:
        documentation_score += 8

    if repo.topics and len(repo.topics) >= 3:
        documentation_score += 6

    if repo.homepage:
        documentation_score += 6

    score += documentation_score
    breakdown["documentation"] += documentation_score

    if documentation_score >= 12:
        signals["good_documentation"] = True

    # --- ACTIVIDAD REAL ---
    days_inactive = calculate_days_inactive(
        repo.last_update
    )

    activity_score = 0

    from .weights import (
        ACTIVITY_REALLY_RECENT,
        ACTIVITY_VERY_RECENT,
        ACTIVITY_RECENT,
        ACTIVITY_MODERATE,
        ACTIVITY_LOW,
    )

    if days_inactive <= 30:
        activity_score = ACTIVITY_REALLY_RECENT
        signals["very_recent_activity"] = True

    elif days_inactive <= 75:
        activity_score = ACTIVITY_VERY_RECENT
        signals["very_recent_activity"] = True

    elif days_inactive <= 150:
        activity_score = ACTIVITY_RECENT
        signals["recent_activity"] = True

    elif days_inactive <= 230:
        activity_score = ACTIVITY_MODERATE
        signals["moderate_activity"] = True

    elif days_inactive <= 365:
        activity_score = ACTIVITY_LOW
        signals["low_activity"] = True

    else:
        activity_score -= INACTIVITY_PENALTY
        signals["low_activity"] = True

    score += activity_score

    if activity_score >= 0:
        breakdown["activity"] += activity_score
    else:
        breakdown["penalties"] += activity_score

    # --- LOW QUALITY REPO DETECTION ---

    repo_name_tokens = tokenize_text(repo.name)

    if any(token in LOW_QUALITY_TERMS for token in repo_name_tokens):

        score -= LOW_QUALITY_REPO_PENALTY
        breakdown["penalties"] -= LOW_QUALITY_REPO_PENALTY

    # --- FORKS ---
    if repo.fork:

        score -= FORK_PENALTY
        breakdown["penalties"] -= FORK_PENALTY

        if repo.stars > 500:

            score += RELEVANT_FORK_BONUS
            breakdown["relevance"] += RELEVANT_FORK_BONUS

            signals["relevant_fork"] = True

        else:
            signals["irrelevant_fork"] = True

    # --- CONFIANZA ---

    confidence = "low"

    positive_signals = 0

    if (
        signals["full_match"]
        or signals["partial_match"]
    ):
        positive_signals += 1

    if (
        signals["very_recent_activity"]
        or signals["recent_activity"]
    ):
        positive_signals += 1

    if signals["good_documentation"]:
        positive_signals += 1

    if (
        signals["medium_popularity"]
        or signals["high_popularity"]
        or signals["elite_popularity"]
    ):
        positive_signals += 1

    if score >= 70 and positive_signals >= 3:
        confidence = "high"

    elif score >= 40 and positive_signals >= 2:
        confidence = "medium"

    # --- RETURN ---

    return {
        "total_score": max(score, 0),
        "confidence": confidence,
        "breakdown": breakdown,
        "signals": signals
    }