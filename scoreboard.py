# scoreboard.py
import streamlit as st
import pandas as pd



from score_calculator import (
    compute_game_points,
    PLACEMENT_POINTS,
    BONUS_STAR_POINTS,
    COIN_THRESHOLD_POINTS,
    COIN_THRESHOLD,
    COIN_THRESHOLD_MAX,
)
from consistency import compute_consistency_bonuses


def compute_game_points_breakdown(game, players):
    """
    Return a detailed breakdown of points per rule, per player, for ONE game.

    Returns:
      breakdown[player] = {
          "placement_pts": int,
          "bonus_star_pts": int,
          "coin_threshold_pts": int,
          "coin_most_pts": int,
          "coin_least_pts": int,
          "items_pts": int,
          "spaces_pts": int,
          "base_total": int,
      }
    """
    results = game["results"]
    breakdown = {p: {} for p in players}

    # Raw coins for most/least logic
    coin_values = {p: int(results[p]["coins"]) for p in players}
    max_coins = max(coin_values.values())
    min_coins = min(coin_values.values())

    for p in players:
        r = results[p]

        # Placement
        placement = int(r["placement"])
        placement_pts = PLACEMENT_POINTS.get(placement, 0)

        # Bonus stars
        bonus_stars = int(r["bonus_stars"])
        bonus_star_pts = bonus_stars * BONUS_STAR_POINTS

        # Coin threshold
        coins = int(r["coins"])
        threshold_units = min(coins // COIN_THRESHOLD, COIN_THRESHOLD_MAX)
        coin_threshold_pts = threshold_units * COIN_THRESHOLD_POINTS

        # Most / least coins
        coin_most_pts = 0
        coin_least_pts = 0
        if coin_values[p] == max_coins and max_coins > 0:
            coin_most_pts = 2
        if coin_values[p] == min_coins:
            coin_least_pts = -1

        # Items & spaces
        items_pts = 1 if r.get("most_items_used", False) else 0
        spaces_pts = 1 if r.get("most_spaces_travelled", False) else 0

        base_total = (
            placement_pts
            + bonus_star_pts
            + coin_threshold_pts
            + coin_most_pts
            + coin_least_pts
            + items_pts
            + spaces_pts
        )

        breakdown[p] = {
            "placement_pts": placement_pts,
            "bonus_star_pts": bonus_star_pts,
            "coin_threshold_pts": coin_threshold_pts,
            "coin_most_pts": coin_most_pts,
            "coin_least_pts": coin_least_pts,
            "items_pts": items_pts,
            "spaces_pts": spaces_pts,
            "base_total": base_total,
        }

    return breakdown


def assign_ranks(total_points_by_player):
    """
    Given a dict {player: total_points}, return dict {player: rank} with ties.
    Uses standard competition ranking (1,2,2,4).
    """
    # Sort players by total points (desc)
    sorted_players = sorted(
        total_points_by_player.items(), key=lambda x: x[1], reverse=True
    )

    ranks = {}
    last_points = None
    last_rank = 0

    for idx, (player, pts) in enumerate(sorted_players, start=1):
        if pts != last_points:
            rank = idx
            last_rank = rank
            last_points = pts
        else:
            rank = last_rank

        ranks[player] = rank

    return ranks

def build_streamlit_cumulative_chart(games_sorted, players):
    """
    Builds a cumulative points line chart using Streamlit native charts.
    X = Game #
    Y = Total cumulative points
    """

    # Initialize running totals
    running_totals = {p: 0 for p in players}
    chart_rows = []

    for g in games_sorted:
        game_id = g["game_id"]
        game_points = g["points"]  # already computed when game was saved

        row = {"Game": game_id}
        for p in players:
            running_totals[p] += int(game_points.get(p, 0))
            row[p] = running_totals[p]

        chart_rows.append(row)

    if not chart_rows:
        st.info("No games available for chart yet.")
        return

    df = pd.DataFrame(chart_rows).set_index("Game")

    st.subheader("Points Progression (Line Graph)")
    st.line_chart(df)


def scoreboard_page(players):
    st.header("Scoreboard")

    games = st.session_state.games

    if not games:
        st.info("No games recorded yet. Add a game on the Calculate Scores page.")
        return

    # ---------- 1. Base points & per-rule breakdown ----------
    base_totals = {p: 0 for p in players}
    per_game_rows = []

    # Win & podium counters
    wins = {p: 0 for p in players}
    podiums = {p: 0 for p in players}

    # Ensure games are in order
    games_sorted = sorted(games, key=lambda g: g.get("game_id", 0))

    build_streamlit_cumulative_chart(games_sorted, players)



    for g in games_sorted:
        game_id = g["game_id"]
        results = g["results"]

        # Detailed rule breakdown for this game
        breakdown = compute_game_points_breakdown(g, players)

        for p in players:
            pl = int(results[p]["placement"])
            br = breakdown[p]

            base_totals[p] += br["base_total"]

            # Wins & podiums
            if pl == 1:
                wins[p] += 1
            if pl in (1, 2, 3):
                podiums[p] += 1

            row = {
                "Game ID": game_id,
                "Player": p,
                "Placement": pl,
                "Placement Pts": br["placement_pts"],
                "Bonus Star Pts": br["bonus_star_pts"],
                "Coin Threshold Pts": br["coin_threshold_pts"],
                "Most Coins Pts": br["coin_most_pts"],
                "Least Coins Pts": br["coin_least_pts"],
                "Items Pts": br["items_pts"],
                "Spaces Pts": br["spaces_pts"],
                "Base Total (this game)": br["base_total"],
            }
            per_game_rows.append(row)

    # ---------- 2. Consistency bonuses ----------
    consistency_totals, per_game_consistency = compute_consistency_bonuses(
        games_sorted, players
    )

    # ---------- 3. Final totals & ranks ----------
    final_totals = {
        p: base_totals[p] + consistency_totals.get(p, 0) for p in players
    }

    ranks = assign_ranks(final_totals)

    standings_rows = []
    for p in players:
        standings_rows.append(
            {
                "Rank": ranks[p],
                "Player": p,
                "Wins": wins[p],
                "Podiums": podiums[p],
                "Base Points": base_totals[p],
                "Consistency Bonus": consistency_totals.get(p, 0),
                "Total Points": final_totals[p],
            }
        )

    standings_df = (
        pd.DataFrame(standings_rows)
        .sort_values(["Rank", "Player"])
        .reset_index(drop=True)
    )

    st.subheader("Overall Standings")
    st.dataframe(standings_df, use_container_width=True)

    # ---------- 4. Per-game breakdown by rule (including consistency) ----------
    st.subheader("Per-game breakdown by rule")

    # Attach per-game consistency bonus & final game total
    for row in per_game_rows:
        gid = row["Game ID"]
        p = row["Player"]
        cb = per_game_consistency.get(p, {}).get(gid, 0)
        row["Consistency Bonus (this game)"] = cb
        row["Total Pts (this game)"] = row["Base Total (this game)"] + cb

    breakdown_df = pd.DataFrame(per_game_rows).sort_values(
        ["Game ID", "Player"]
    )
    st.dataframe(breakdown_df, use_container_width=True)

    # Expose standings for summary page
    st.session_state.current_standings = standings_df


