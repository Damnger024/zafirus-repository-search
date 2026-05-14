QUERY_EXPANSIONS = {


    "auth": [
        "authentication",
        "authorization",
        "jwt",
        "oauth",
        "security"
    ],


    "api": [
        "rest",
        "backend",
        "http"
    ],


    "database": [
        "sql",
        "postgres",
        "mysql",
        "orm"
    ],


    "ai": [
        "machine-learning",
        "llm",
        "openai",
        "neural-network"
    ]
}

def expand_query(query: str):

    expanded_terms = [query]

    query_lower = query.lower()

    for keyword, expansions in QUERY_EXPANSIONS.items():

        if keyword in query_lower:
            expanded_terms.extend(expansions)

    return expanded_terms
