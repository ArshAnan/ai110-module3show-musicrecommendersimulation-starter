import csv
from typing import List, Dict, Tuple
from dataclasses import dataclass


@dataclass
class Song:
    """Represents a song and its audio/metadata attributes."""
    id: int
    title: str
    artist: str
    genre: str
    mood: str
    energy: float
    tempo_bpm: float
    valence: float
    danceability: float
    acousticness: float


@dataclass
class UserProfile:
    """Represents a user's taste preferences used for scoring."""
    favorite_genre: str
    favorite_mood: str
    target_energy: float
    likes_acoustic: bool


class Recommender:
    """OOP interface for scoring and ranking songs against a UserProfile."""

    def __init__(self, songs: List[Song]):
        self.songs = songs

    def recommend(self, user: UserProfile, k: int = 5) -> List[Song]:
        """Return the top-k Song objects ranked by score for the given user."""
        return sorted(self.songs, key=lambda s: self._score(user, s), reverse=True)[:k]

    def explain_recommendation(self, user: UserProfile, song: Song) -> str:
        """Return a human-readable string explaining why a song was recommended."""
        reasons = []

        if song.genre == user.favorite_genre:
            reasons.append(f"genre match ({song.genre}) +2.0")
        if song.mood == user.favorite_mood:
            reasons.append(f"mood match ({song.mood}) +1.0")

        energy_pts = 1.5 * (1 - abs(song.energy - user.target_energy))
        reasons.append(f"energy fit +{energy_pts:.2f}")

        if user.likes_acoustic and song.acousticness > 0.6:
            reasons.append("acoustic match +0.5")

        return "; ".join(reasons) if reasons else "no strong match found"

    def _score(self, user: UserProfile, song: Song) -> float:
        """Compute the numeric score for a single Song against a UserProfile."""
        score = 0.0
        if song.genre == user.favorite_genre:
            score += 2.0
        if song.mood == user.favorite_mood:
            score += 1.0
        score += 1.5 * (1 - abs(song.energy - user.target_energy))
        if user.likes_acoustic and song.acousticness > 0.6:
            score += 0.5
        return score


# ---------------------------------------------------------------------------
# Functional API (used by src/main.py)
# ---------------------------------------------------------------------------

def load_songs(csv_path: str) -> List[Dict]:
    """Load songs from a CSV file and return a list of dicts with typed values."""
    songs = []
    with open(csv_path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            songs.append({
                "id":           int(row["id"]),
                "title":        row["title"],
                "artist":       row["artist"],
                "genre":        row["genre"],
                "mood":         row["mood"],
                "energy":       float(row["energy"]),
                "tempo_bpm":    int(row["tempo_bpm"]),
                "valence":      float(row["valence"]),
                "danceability": float(row["danceability"]),
                "acousticness": float(row["acousticness"]),
            })
    return songs


def score_song(user_prefs: Dict, song: Dict) -> Tuple[float, List[str]]:
    """
    Score a single song against user preferences.

    Algorithm recipe:
      +2.0  genre exact match
      +1.0  mood exact match
      +0–1.5  energy closeness:  1.5 × (1 − |song.energy − user.energy|)
      +0–0.5  valence closeness: 0.5 × (1 − |song.valence − user.valence|)
      +0.5  acoustic bonus if user.likes_acoustic and song.acousticness > 0.6

    Returns (score, reasons) where reasons is a list of plain-English strings.
    """
    score = 0.0
    reasons = []

    # Genre match: +2.0
    if song["genre"] == user_prefs.get("genre"):
        score += 2.0
        reasons.append(f"genre match ({song['genre']}) +2.0")

    # Mood match: +1.0
    if song["mood"] == user_prefs.get("mood"):
        score += 1.0
        reasons.append(f"mood match ({song['mood']}) +1.0")

    # Energy closeness: 0 – 1.5
    energy_pts = 1.5 * (1 - abs(song["energy"] - user_prefs["energy"]))
    score += energy_pts
    reasons.append(f"energy fit +{energy_pts:.2f}")

    # Valence closeness: 0 – 0.5 (only when user_prefs includes valence)
    if "valence" in user_prefs:
        valence_pts = 0.5 * (1 - abs(song["valence"] - user_prefs["valence"]))
        score += valence_pts
        reasons.append(f"valence fit +{valence_pts:.2f}")

    # Acoustic bonus: +0.5
    if user_prefs.get("likes_acoustic") and song["acousticness"] > 0.6:
        score += 0.5
        reasons.append("acoustic match +0.5")

    return score, reasons


def recommend_songs(
    user_prefs: Dict, songs: List[Dict], k: int = 5
) -> List[Tuple[Dict, float, str]]:
    """
    Score every song, rank by score descending, and return the top-k results.

    Uses sorted() (non-destructive) rather than .sort() so the original songs
    list is never mutated — callers can safely reuse it for different profiles.

    Returns a list of (song_dict, score, explanation) tuples.
    """
    scored = []
    for song in songs:
        score, reasons = score_song(user_prefs, song)
        explanation = " | ".join(reasons)
        scored.append((song, score, explanation))

    # sorted() returns a new list; .sort() would mutate in place.
    ranked = sorted(scored, key=lambda item: item[1], reverse=True)
    return ranked[:k]
