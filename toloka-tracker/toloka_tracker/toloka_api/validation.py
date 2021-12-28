from toloka_tracker.toloka_api.api import *
from toloka_tracker.toloka_api.models import *


def track_pool(pool: TolokaPool, acceptance_rate: float):
    accepted, rejected = count_pool_stats(pool.id)

    if accepted == 0 or rejected == 0:
        return True

    return check_pool(accepted, rejected, acceptance_rate)


def check_pool(accepted: int, rejected: int, min_acceptance_rate: float):
    if accepted == 0 and rejected == 0:
        return True

    return min_acceptance_rate <= accepted / (accepted + rejected)


def track_project(project: TolokaProject, max_pools_count: int):
    pools = get_pools(project.id, PoolStatus.OPEN)

    return check_project(pools, max_pools_count)


def check_project(pools, max_pools_count: int):
    return max_pools_count >= len(pools)