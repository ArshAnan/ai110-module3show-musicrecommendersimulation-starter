"""
Command-line runner for the Music Recommender Simulation.

Run with:
    python -m src.main
"""

from src.recommender import load_songs, recommend_songs

# ---------------------------------------------------------------------------
# User profiles used for evaluation
# ---------------------------------------------------------------------------

PROFILES = [
    {
        "label": "Chill Lofi Listener",
        "prefs": {
            "genre": "lofi",
            "mood": "chill",
            "energy": 0.40,
            "valence": 0.60,
            "likes_acoustic": True,
        },
    },
    {
        "label": "High-Energy Pop Fan",
        "prefs": {
            "genre": "pop",
            "mood": "happy",
            "energy": 0.85,
            "valence": 0.82,
            "likes_acoustic": False,
        },
    },
    {
        "label": "Intense Rock Head",
        "prefs": {
            "genre": "rock",
            "mood": "intense",
            "energy": 0.90,
            "valence": 0.45,
            "likes_acoustic": False,
        },
    },
    # --- Adversarial profiles ---
    {
        "label": "ADVERSARIAL: High Energy + Sad (conflicting vibe)",
        "prefs": {
            "genre": "folk",
            "mood": "sad",
            "energy": 0.92,
            "valence": 0.30,
            "likes_acoustic": True,
        },
    },
    {
        "label": "ADVERSARIAL: Genre Not In Catalog (metal)",
        "prefs": {
            "genre": "metal",
            "mood": "intense",
            "energy": 0.95,
            "valence": 0.25,
            "likes_acoustic": False,
        },
    },
]


def print_recommendations(label: str, recommendations: list, k: int = 5) -> None:
    """Print a formatted recommendation table for one user profile."""
    bar = "=" * 70
    print(f"\n{bar}")
    print(f"  Profile: {label}")
    print(bar)
    print(f"  {'Rank':<5} {'Title':<25} {'Artist':<22} {'Score':>5}")
    print(f"  {'-' * 62}")
    for rank, (song, score, explanation) in enumerate(recommendations, start=1):
        print(f"  {rank:<5} {song['title']:<25} {song['artist']:<22} {score:>5.2f}")
        for reason in explanation.split(" | "):
            print(f"         → {reason}")
        print()


def main(experiment: bool = False) -> None:
    songs = load_songs("data/songs.csv")
    print(f"\nLoaded {len(songs)} songs.")

    if experiment:
        # Weight-shift experiment: halve genre, double energy.
        # This tests whether energy similarity drives better recommendations
        # when genre dominance is reduced.
        print("\n*** EXPERIMENT: genre weight ×0.5 | energy weight ×2 ***")
        from src.recommender import score_song as _base_score

        def experimental_score(user_prefs, song):
            """Modified scorer: genre=1.0, energy=3.0, rest unchanged."""
            score = 0.0
            reasons = []
            if song["genre"] == user_prefs.get("genre"):
                score += 1.0          # was 2.0
                reasons.append(f"genre match ({song['genre']}) +1.0")
            if song["mood"] == user_prefs.get("mood"):
                score += 1.0
                reasons.append(f"mood match ({song['mood']}) +1.0")
            energy_pts = 3.0 * (1 - abs(song["energy"] - user_prefs["energy"]))  # was 1.5
            score += energy_pts
            reasons.append(f"energy fit +{energy_pts:.2f}")
            if "valence" in user_prefs:
                valence_pts = 0.5 * (1 - abs(song["valence"] - user_prefs["valence"]))
                score += valence_pts
                reasons.append(f"valence fit +{valence_pts:.2f}")
            if user_prefs.get("likes_acoustic") and song["acousticness"] > 0.6:
                score += 0.5
                reasons.append("acoustic match +0.5")
            return score, reasons

        # Run only the first 3 profiles for the experiment
        for profile in PROFILES[:3]:
            scored = []
            for song in songs:
                score, reasons = experimental_score(profile["prefs"], song)
                scored.append((song, score, " | ".join(reasons)))
            ranked = sorted(scored, key=lambda x: x[1], reverse=True)[:5]
            print_recommendations(f"[EXP] {profile['label']}", ranked)
        return

    # Normal run: all profiles with standard weights
    for profile in PROFILES:
        results = recommend_songs(profile["prefs"], songs, k=5)
        print_recommendations(profile["label"], results)


if __name__ == "__main__":
    import sys
    experiment_mode = "--experiment" in sys.argv
    main(experiment=experiment_mode)
