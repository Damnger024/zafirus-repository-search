from models.repository import Repository

MIN_STARS = 3
MIN_FORK_STARS = 30


def filter_repositories(
    repositories: list[Repository]
):

    # si GitHub devolvió pocos resultados,
    # no filtrar agresivamente
    if len(repositories) < 15:
        return repositories

    filtered_repositories = []

    for repo in repositories:

        if repo.archived:
            continue

        if repo.stars < MIN_STARS:
            continue

        if repo.fork and repo.stars < MIN_FORK_STARS:
            continue

        filtered_repositories.append(repo)

    return filtered_repositories