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

NEGATIVE_INTENT_TERMS = {
    "demo",
    "tutorial",
    "example",
    "boilerplate",
    "starter",
    "template",
    "awesome",
    "roadmap",
    "resources",
    "list",
    "cracker",
    "scanner",
    "pentest",
    "exploit",
    "attack",
    "ctf"
}

POSITIVE_INTENT_TERMS = {
    "library",
    "framework",
    "sdk",
    "extension",
    "client",
    "toolkit",
    "implementation",
    "wrapper",
    "plugin",
    "middleware"
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

    # =========================
    # NORMALIZED TEXT
    # =========================

    query_lower = query.lower().strip()

    query_tokens = tokenize_text(query)

    repo_name = (repo.name or "").lower()
    repo_description = (repo.description or "").lower()
    repo_topics = " ".join(repo.topics).lower()

    name_tokens = tokenize_text(repo.name or "")
    description_tokens = tokenize_text(repo.description or "")
    topic_tokens = tokenize_text(repo_topics)

    # =========================
    # STARS
    # =========================

    stars = repo.stars
    stars_score = 0

    if stars >= 5000:

        stars_score = 25
        signals["elite_popularity"] = True

    elif stars >= 2000:

        stars_score = 20
        signals["high_popularity"] = True

    elif stars >= 1000:

        stars_score = 17
        signals["medium_popularity"] = True

    elif stars >= 500:

        stars_score = 14

    elif stars >= 100:

        stars_score = 10

    else:

        stars_score = 5

    score += stars_score
    breakdown["stars"] += stars_score

    # =========================
    # RELEVANCE
    # =========================

    valid_query_tokens = [
        token
        for token in query_tokens
        if len(token) >= 3
    ]

    matched_tokens = 0.0

    # separated relevance buckets
    name_score = 0
    topic_score = 0
    description_score = 0
    coverage_bonus = 0
    intent_bonus = 0
    phrase_score = 0

    # =========================
    # EXACT PHRASE MATCH
    # =========================

    if query_lower in repo_name:
        phrase_score += 14

    elif query_lower in repo_topics:
        phrase_score += 10

    elif query_lower in repo_description:
        phrase_score += 3

    # =========================
    # TOKEN MATCHES
    # =========================

    strong_matches = 0

    for token in valid_query_tokens:

        token_strength = 0

        # repo name
        if token in name_tokens:
            name_score += 5
            token_strength += 1.0

        # repo topics
        if token in topic_tokens:
            topic_score += 4
            token_strength += 0.9

        # repo description
        if token in description_tokens:
            description_score += 0.5
            token_strength += 0.15

        if token_strength >= 0.9:
            strong_matches += 1

        matched_tokens += min(
            token_strength,
            1.0
        )

    # =========================
    # COVERAGE BONUS
    # =========================

    coverage_ratio = 0

    if valid_query_tokens:

        coverage_ratio = (
            matched_tokens / len(valid_query_tokens)
        )

        # casi todos los términos encontrados
        if coverage_ratio >= 0.85:
            coverage_bonus = 8

        # buena coincidencia general
        elif coverage_ratio >= 0.60:
            coverage_bonus = 5

        # coincidencia usable
        elif coverage_ratio >= 0.35:
            coverage_bonus = 2

    # =========================
    # STRONG MATCH BONUS
    # =========================

    if strong_matches >= len(valid_query_tokens):
        coverage_bonus += 6

    elif strong_matches >= 2:
        coverage_bonus += 4

    elif strong_matches >= 1:
        coverage_bonus += 2

    # =========================
    # TOPICAL FOCUS BONUS
    # =========================

    name_match_count = 0
    topic_match_count = 0

    for token in valid_query_tokens:

        if token in name_tokens:
            name_match_count += 1

        if token in topic_tokens:
            topic_match_count += 1

    # el nombre define muchísimo el propósito
    name_score += name_match_count * 2

    # topics ayudan bastante
    topic_score += topic_match_count * 2

    # =========================
    # REPOSITORY INTENT SIGNALS
    # =========================

    repo_text_tokens = set(
        name_tokens
        + description_tokens
        + topic_tokens
    )

    positive_intent_matches = 0
    negative_intent_matches = 0

    POSITIVE_INTENT_TERMS = {
        "library",
        "framework",
        "sdk",
        "extension",
        "client",
        "toolkit",
        "implementation",
        "wrapper",
        "plugin",
        "middleware"
    }

    for term in POSITIVE_INTENT_TERMS:

        if term in repo_text_tokens:
            positive_intent_matches += 1

    for term in NEGATIVE_INTENT_TERMS:

        if term in repo_text_tokens:
            negative_intent_matches += 1

    intent_bonus += positive_intent_matches * 1.5
    intent_bonus -= negative_intent_matches * 4

    # =========================
    # NORMALIZE BUCKETS
    # =========================

    name_score = min(name_score, 12)
    topic_score = min(topic_score, 10)
    description_score = min(description_score, 3)
    coverage_bonus = min(coverage_bonus, 10)

    intent_bonus = max(min(intent_bonus, 6), -10)

    phrase_score = min(phrase_score, 14)

    # =========================
    # LOW QUALITY MULTIPLIER
    # =========================

    low_quality_matches = 0

    for term in LOW_QUALITY_TERMS:

        if term in repo_text_tokens:
            low_quality_matches += 1

    quality_multiplier = 1.0

    if low_quality_matches >= 1:
        quality_multiplier = 0.82

    if low_quality_matches >= 2:
        quality_multiplier = 0.7

    # =========================
    # FINAL RELEVANCE SCORE
    # =========================

    raw_relevance_score = (
        name_score
        + topic_score
        + description_score
        + coverage_bonus
        + intent_bonus
        + phrase_score
    )

    relevance_score = (
        raw_relevance_score
        * quality_multiplier
    )

    relevance_score = round(
        max(
            0,
            min(
                relevance_score,
                RELEVANCE_FULL_MATCH
            )
        )
    )

    score += relevance_score
    breakdown["relevance"] += relevance_score

    # =========================
    # RELEVANCE SIGNALS
    # =========================

    if relevance_score >= 26:
        signals["full_match"] = True

    elif relevance_score >= 12:
        signals["partial_match"] = True

    # =========================
    # DOCUMENTATION
    # =========================

    documentation_score = 0

    if repo.description and len(repo.description.strip()) >= 20:
        documentation_score += 5

    if repo.topics and len(repo.topics) >= 3:
        documentation_score += 4

    if repo.homepage:
        documentation_score += 3

    score += documentation_score
    breakdown["documentation"] += documentation_score

    if documentation_score >= 8:
        signals["good_documentation"] = True

    # =========================
    # ACTIVITY
    # =========================

    days_inactive = calculate_days_inactive(
        repo.last_update
    )

    activity_score = 0

    if days_inactive <= 30:

        activity_score = 18
        signals["very_recent_activity"] = True

    elif days_inactive <= 75:

        activity_score = 14
        signals["very_recent_activity"] = True

    elif days_inactive <= 150:

        activity_score = 10
        signals["recent_activity"] = True

    elif days_inactive <= 230:

        activity_score = 6
        signals["moderate_activity"] = True

    elif days_inactive <= 365:

        activity_score = 2
        signals["low_activity"] = True

    else:

        activity_score -= INACTIVITY_PENALTY
        signals["low_activity"] = True

    score += activity_score

    if activity_score >= 0:
        breakdown["activity"] += activity_score

    else:
        breakdown["penalties"] += activity_score

    # =========================
    # LOW QUALITY DETECTION
    # =========================

    repo_name_tokens = tokenize_text(repo.name)

    if any(
        token in LOW_QUALITY_TERMS
        for token in repo_name_tokens
    ):

        score -= LOW_QUALITY_REPO_PENALTY
        breakdown["penalties"] -= LOW_QUALITY_REPO_PENALTY

    # =========================
    # FORKS
    # =========================

    if repo.fork:

        score -= FORK_PENALTY
        breakdown["penalties"] -= FORK_PENALTY

        if repo.stars > 500:

            score += RELEVANT_FORK_BONUS
            breakdown["relevance"] += RELEVANT_FORK_BONUS

            signals["relevant_fork"] = True

        else:

            signals["irrelevant_fork"] = True

    # =========================
    # AUTHORITY ADJUSTMENT
    # =========================

    authority_multiplier = 1.0

    if repo.stars < 50:
        authority_multiplier = 0.88

    elif repo.stars < 150:
        authority_multiplier = 0.93

    score *= authority_multiplier

    # =========================
    # CONFIDENCE
    # =========================

    confidence = "low"

    if relevance_score >= 28 and score >= 70:
        confidence = "high"

    elif relevance_score >= 18 and score >= 45:
        confidence = "medium"

    # =========================
    # ROUNDING
    # =========================

    score = round(score, 1)
    relevance_score = round(relevance_score, 1)

    breakdown["relevance"] = relevance_score

    # =========================
    # SCORE NORMALIZATION
    # =========================

    normalized_score = score

    if normalized_score >= 65:
        normalized_score += 8

    elif normalized_score >= 50:
        normalized_score += 5

    elif normalized_score >= 35:
        normalized_score += 2

    normalized_score = min(
        round(normalized_score),
        100
    )

    # =========================
    # RETURN
    # =========================

    return {
        "total_score": normalized_score,
        "confidence": confidence,
        "breakdown": breakdown,
        "signals": signals
    }