def generate_explanation(repo, query):

    reasons = []

    # --- STARS ---
    if repo.signals["elite_popularity"]:
        reasons.append("repositorio extremadamente popular")

    elif repo.signals["high_popularity"]:
        reasons.append("alta popularidad")

    elif repo.signals["medium_popularity"]:
        reasons.append("popularidad moderada")

    # --- ACTIVIDAD ---
    if repo.signals["very_recent_activity"]:
        reasons.append("muy activo recientemente")

    elif repo.signals["recent_activity"]:
        reasons.append("actividad reciente")

    elif repo.signals["moderate_activity"]:
        reasons.append("actividad moderada")

    elif repo.signals["low_activity"]:
        reasons.append("poca actividad reciente")

    # --- RELEVANCIA ---
    if repo.signals["full_match"]:
        reasons.append("alta coincidencia con la búsqueda")

    elif repo.signals["partial_match"]:
        reasons.append("coincidencia parcial con la búsqueda")

    # --- ARCHIVED ---
    if repo.signals["archived"]:
        reasons.append("penalizado por estar archivado")

    # --- FORKS ---
    if repo.signals["relevant_fork"]:
        reasons.append("fork relevante con buena adopción")

    elif repo.signals["irrelevant_fork"]:
        reasons.append("fork con menor relevancia")

    # --- BONUS ---
    if repo.signals["good_documentation"]:
        reasons.append("documentación clara")

    return reasons