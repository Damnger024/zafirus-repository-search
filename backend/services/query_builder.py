from services.query_expander import expand_query

def build_query(query: str, languages: list[str]):

    expanded_terms = expand_query(query)

    combined_query = " OR ".join(expanded_terms)

    language_query = " ".join(
        [f"language:{language}" for language in languages]
    )

    search_query = (
        f"{combined_query} {language_query}"
    )

    return search_query
