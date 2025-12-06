# consistency.py

def compute_consistency_bonuses(games, players):
    bonuses = {p: 0 for p in players}
    if not games:
        return bonuses

    sorted_games = sorted(games, key=lambda g: g["game_id"])

    for player in players:
        placements = [g["results"][player]["placement"] for g in sorted_games]
        n = len(placements)
        total = 0

        # Back-to-back Top 2 → +2
        for i in range(1, n):
            if placements[i] <= 2 and placements[i - 1] <= 2:
                total += 2

        # Top 2 in 3 straight → +3
        for i in range(2, n):
            if placements[i] <= 2 and placements[i - 1] <= 2 and placements[i - 2] <= 2:
                total += 3

        # No 4th place in 5 → +2
        for i in range(4, n):
            window = placements[i - 4:i + 1]
            if all(p != 4 for p in window):
                total += 2

        bonuses[player] = total

    return bonuses
