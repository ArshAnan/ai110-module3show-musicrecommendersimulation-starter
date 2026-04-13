# 🎵 Music Recommender Simulation

## Project Summary

In this project you will build and explain a small music recommender system.

Your goal is to:

- Represent songs and a user "taste profile" as data
- Design a scoring rule that turns that data into recommendations
- Evaluate what your system gets right and wrong
- Reflect on how this mirrors real world AI recommenders

This version builds a content-based music recommender that scores songs from a 10-song catalog against a user's taste profile (genre, mood, energy preference, and acoustic preference). It ranks songs by a weighted similarity score and returns the top matches with a plain-language explanation of why each song was chosen.

---

## How The System Works

Real-world music recommenders like Spotify combine two strategies. **Collaborative filtering** finds patterns across millions of users ("people who liked X also liked Y"), while **content-based filtering** compares the actual attributes of songs — tempo, energy, mood, genre — against a user's known preferences. At scale, Spotify layers deep learning on top of raw audio to detect sonic similarity beyond what any single label captures. This simulator focuses on the content-based approach: it scores every song numerically against a user profile and returns the best matches.

### Song features used

Each `Song` object stores these attributes:

- `genre` — categorical (pop, lofi, rock, ambient, etc.)
- `mood` — categorical (happy, chill, intense, relaxed, moody, focused)
- `energy` — float 0–1 (how driving/intense the track feels)
- `valence` — float 0–1 (musical positivity/happiness)
- `acousticness` — float 0–1 (acoustic vs. electronic character)
- `danceability`, `tempo_bpm` — stored but used as secondary signals

### UserProfile stores

- `favorite_genre` — the genre to reward most
- `favorite_mood` — the mood/vibe to reward
- `target_energy` — ideal energy level (0–1)
- `likes_acoustic` — boolean preference for acoustic sound

### Scoring Rule (one song)

For categorical features, a match adds a flat bonus. For numerical features, closeness is rewarded using `1 - |song_value - user_preference|` so a perfect match scores 1.0 and a complete mismatch scores 0.0:

```
score = 3.0 × (genre match)
      + 2.0 × (mood match)
      + 2.0 × (1 - |song.energy - user.target_energy|)
      + 1.0 × (1 - |song.valence - 0.7|)   ← default positivity target
      + 1.0 × (acoustic bonus if user.likes_acoustic)
```

Genre carries the highest weight (3 pts) because listeners tend to stay within genres most consistently. Mood is second (2 pts). Energy closeness matters more than valence (2 vs. 1 pt) because energy strongly predicts activity fit.

### Ranking Rule (choosing what to show)

Once every song has a score, the system sorts the full list in descending order and returns the top-k results. The Scoring Rule answers "how good is *this* song?"; the Ranking Rule answers "which songs do I actually show?" — two separate operations chained together.

---

## Getting Started

### Setup

1. Create a virtual environment (optional but recommended):

   ```bash
   python -m venv .venv
   source .venv/bin/activate      # Mac or Linux
   .venv\Scripts\activate         # Windows

2. Install dependencies

```bash
pip install -r requirements.txt
```

3. Run the app:

```bash
python -m src.main
```

### Running Tests

Run the starter tests with:

```bash
pytest
```

You can add more tests in `tests/test_recommender.py`.

---

## Experiments You Tried

Use this section to document the experiments you ran. For example:

- What happened when you changed the weight on genre from 2.0 to 0.5
- What happened when you added tempo or valence to the score
- How did your system behave for different types of users

---

## Limitations and Risks

Summarize some limitations of your recommender.

Examples:

- It only works on a tiny catalog
- It does not understand lyrics or language
- It might over favor one genre or mood

You will go deeper on this in your model card.

---

## Reflection

Read and complete `model_card.md`:

[**Model Card**](model_card.md)

Write 1 to 2 paragraphs here about what you learned:

- about how recommenders turn data into predictions
- about where bias or unfairness could show up in systems like this


---

## 7. `model_card_template.md`

Combines reflection and model card framing from the Module 3 guidance. :contentReference[oaicite:2]{index=2}  

```markdown
# 🎧 Model Card - Music Recommender Simulation

## 1. Model Name

Give your recommender a name, for example:

> VibeFinder 1.0

---

## 2. Intended Use

- What is this system trying to do
- Who is it for

Example:

> This model suggests 3 to 5 songs from a small catalog based on a user's preferred genre, mood, and energy level. It is for classroom exploration only, not for real users.

---

## 3. How It Works (Short Explanation)

Describe your scoring logic in plain language.

- What features of each song does it consider
- What information about the user does it use
- How does it turn those into a number

Try to avoid code in this section, treat it like an explanation to a non programmer.

---

## 4. Data

Describe your dataset.

- How many songs are in `data/songs.csv`
- Did you add or remove any songs
- What kinds of genres or moods are represented
- Whose taste does this data mostly reflect

---

## 5. Strengths

Where does your recommender work well

You can think about:
- Situations where the top results "felt right"
- Particular user profiles it served well
- Simplicity or transparency benefits

---

## 6. Limitations and Bias

Where does your recommender struggle

Some prompts:
- Does it ignore some genres or moods
- Does it treat all users as if they have the same taste shape
- Is it biased toward high energy or one genre by default
- How could this be unfair if used in a real product

---

## 7. Evaluation

How did you check your system

Examples:
- You tried multiple user profiles and wrote down whether the results matched your expectations
- You compared your simulation to what a real app like Spotify or YouTube tends to recommend
- You wrote tests for your scoring logic

You do not need a numeric metric, but if you used one, explain what it measures.

---

## 8. Future Work

If you had more time, how would you improve this recommender

Examples:

- Add support for multiple users and "group vibe" recommendations
- Balance diversity of songs instead of always picking the closest match
- Use more features, like tempo ranges or lyric themes

---

## 9. Personal Reflection

A few sentences about what you learned:

- What surprised you about how your system behaved
- How did building this change how you think about real music recommenders
- Where do you think human judgment still matters, even if the model seems "smart"

