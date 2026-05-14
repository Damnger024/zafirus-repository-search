QUERY_EXPANSIONS = {
    "auth": [
        "jwt",
        "oauth",
        "authorization"
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

    query_tokens = query.lower().split()

    for keyword, expansions in QUERY_EXPANSIONS.items():

        # MATCH EXACTO DE TOKEN
        if keyword in query_tokens:

            for expansion in expansions:

                if expansion not in expanded_terms:
                    expanded_terms.append(expansion)

    return expanded_terms