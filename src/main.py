"""
Command-line runner for the Music Recommender Simulation.

Run with:
    python -m src.main
"""

from src.recommender import load_songs, recommend_songs


def main() -> None:
    songs = load_songs("data/songs.csv")
    print(f"Loaded {len(songs)} songs.\n")

    # Taste profile: a late-night lofi listener who values chill, acoustic, low-energy tracks.
    # favorite_genre / favorite_mood are categorical matches (exact string comparison).
    # target_energy and target_valence are on a 0.0–1.0 scale; scorer rewards closeness.
    # likes_acoustic adds a bonus when acousticness > 0.6.
    user_prefs = {
        "genre": "lofi",
        "mood": "chill",
        "energy": 0.40,
        "valence": 0.60,
        "likes_acoustic": True,
    }

    print("User profile:")
    for key, value in user_prefs.items():
        print(f"  {key}: {value}")
    print()

    recommendations = recommend_songs(user_prefs, songs, k=5)

    print(f"Top {len(recommendations)} recommendations:\n")
    print(f"{'Rank':<5} {'Title':<25} {'Artist':<22} {'Score':>5}")
    print("-" * 65)

    for rank, (song, score, explanation) in enumerate(recommendations, start=1):
        print(f"{rank:<5} {song['title']:<25} {song['artist']:<22} {score:>5.2f}")
        # Print each reason on its own indented line
        for reason in explanation.split(" | "):
            print(f"       → {reason}")
        print()


if __name__ == "__main__":
    main()
