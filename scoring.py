# scoring.py

def placement_points(place: int) -> int:
    mapping = {1: 10, 2: 6, 3: 3, 4: 0}
    return mapping.get(place, 0)

def bonus_star_points(stars: int) -> int:
    return stars * 2

def coin_points(coins: int, most: bool, least: bool) -> int:
    pts = 0
    if most:
        pts += 2
    if least:
        pts -= 1
    pts += min(coins // 30, 3)
    return pts

def minigame_points(rank: str) -> int:
    if rank == "most":
        return 3
    if rank == "second":
        return 1
    return 0

def compute_game_points(results: dict) -> dict:
    """
    results[player] = {
        placement, bonus_stars, coins, most_coins, least_coins, minigame_rank
    }
    """
    totals = {}

    for player, rec in results.items():
        base = placement_points(rec["placement"])
        bonus = bonus_star_points(rec["bonus_stars"])
        coins = coin_points(rec["coins"], rec["most_coins"], rec["least_coins"])
        mini = minigame_points(rec["minigame_rank"])

        totals[player] = base + bonus + coins + mini

    return totals
