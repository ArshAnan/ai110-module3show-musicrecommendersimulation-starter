# Model Card: Music Recommender Simulation

## 1. Model Name

**VibeFinder 1.0**

---

## 2. Goal / Task

VibeFinder 1.0 tries to answer one question: **given what a listener says they like, which
songs in the catalog are most likely to match their taste?** It does this by assigning a
numeric score to every song and returning the highest-scoring ones.

### Intended Use

This system is designed for classroom exploration. It demonstrates how a content-based
filtering algorithm works — how song attributes like genre, mood, and energy can be
compared to a user profile to produce a ranked list of suggestions. Students and educators
can use it to learn about scoring logic, weight design, and the trade-offs involved in
building simple recommenders.

### Non-Intended Use

VibeFinder 1.0 should **not** be used as a real music recommendation product. Specifically:

- **Do not use it for actual users who expect personalized results.** The catalog is 18 songs,
  the user profile never learns from listening history, and the scoring weights were chosen
  manually — not trained on real listener data.
- **Do not use it to make claims about musical taste.** It has no understanding of audio
  itself; it only matches text labels and numbers. Two folk songs can sound completely
  different and still score identically.
- **Do not use it where fairness or representation matters.** The catalog heavily
  over-represents English-language streaming genres and has zero coverage of many global
  music traditions. A user whose favorite genre is not in the catalog will always receive
  worse results than a lofi fan.

---

## 3. How the Model Works

Imagine you are a music store clerk who knows your customer's taste. Every time a new
customer walks in, you mentally compare each record in the store to what they told you
they like. For each record you ask five questions:

1. Is this the same genre they asked for? If yes, that record earns 2 bonus points.
2. Does it match the mood they want? If yes, 1 more point.
3. How close is this record's energy to what they want? You give between 0 and 1.5 points
   depending on how close the match is — a perfect energy match earns the full 1.5.
4. How close is the positivity/happiness of the record to what they want? Up to 0.5 points.
5. Did they say they like acoustic music? If yes and this record is acoustic, add 0.5 points.

After scoring every record, you hand over the five with the highest totals. That is
exactly what VibeFinder 1.0 does — automatically, for all 18 songs at once.

Maximum possible score: **5.5 points**.

---

## 4. Data

The catalog contains **18 songs** across 10 genres: pop, lofi, rock, ambient, jazz,
synthwave, indie pop, r&b, classical, hip-hop, country, electronic, folk, latin, and soul.
Moods covered: happy, chill, intense, relaxed, moody, focused, romantic, melancholic,
energetic, peaceful, sad, uplifting.

8 songs were added to the original 10-song starter file to cover genres and moods that
were missing. No songs were removed.

Whose taste does this reflect? The dataset skews toward genres that are common in
English-language streaming platforms — lofi, pop, and rock each have multiple entries,
while genres like classical (1 song) and metal (0 songs) are barely represented or
completely absent. A fan of classical or metal would see this immediately.

---

## 5. Strengths

- **Clear-cut profiles get great results.** A "Chill Lofi Listener" profile immediately
  surfaces all three lofi songs in the top 3, all of which match on energy and acousticness
  too. The recommendations feel intuitive and correct.

- **Explanations are transparent.** Every recommendation comes with a breakdown of exactly
  why each point was awarded. A user can read "genre match (+2.0), energy fit +1.47" and
  understand the logic without reading any code.

- **Energy closeness works as intended.** The formula `1 - |song_energy - user_energy|`
  means a low-energy user gets low-energy songs rewarded, not penalized. A gym playlist
  user (energy 0.85) correctly sees Gym Hero and Sunrise City at the top.

- **The "genre not in catalog" case degrades gracefully.** When a user asks for "metal"
  (which has no songs in the catalog), the system falls back to mood and energy signals
  and surfaces reasonable alternatives (intense, high-energy tracks).

---

## 6. Limitations and Bias

**Genre dominance creates a filter bubble.** Genre is worth 2 points out of 5.5 maximum —
more than any single numerical feature. In the adversarial test with a user who wanted
"folk + sad + high energy (0.92)", the system returned Hollow Bones (folk, sad, energy 0.30)
as the top result. That song is *completely wrong* for the user's energy need — it is a soft
acoustic track — but it still won because the genre and mood labels alone outweighed the
severe energy mismatch. In a real app, this user would immediately skip that song.

**Mood categories are binary, not a spectrum.** The system treats "relaxed" and "chill" as
completely different moods and gives zero credit for proximity. A user asking for "relaxed"
music gets no benefit from songs labelled "chill" even though most people would consider
them interchangeable. This forces the system into rigid buckets rather than fluid taste.

**Catalog size amplifies genre skew.** Lofi has 3 songs, pop has 2, and most other genres
have just 1. A lofi fan will always see 3 lofi songs in their top 5 because there is
nothing else close. This is not a sign of a smart algorithm — it is a side effect of a tiny
dataset. At Spotify scale, 3 vs. 30,000 songs in a genre actually matters.

**Valence and danceability carry little weight.** Valence is capped at 0.5 points, and
danceability is not scored at all. A user who wants to dance will not be served well. These
features are collected in the data but barely used by the algorithm.

**No diversity or novelty.** The system always returns the closest matches with no
mechanism to surface surprising but good songs. A real recommender would intentionally
mix in one or two "stretch" recommendations alongside safe bets.

---

## 7. Evaluation

### Profiles tested

| Profile | Label | Key observation |
|---|---|---|
| 1 | Chill Lofi Listener | Top 3 are all lofi — intuitive and correct |
| 2 | High-Energy Pop Fan | Sunrise City ranks #1; Gym Hero ranks #2 despite not matching mood because genre match outweighs mood mismatch |
| 3 | Intense Rock Head | Storm Runner ranks #1 correctly; #2 is an electronic song (Bass Ritual) — rock fan gets a non-rock result |
| 4 | ADVERSARIAL: High Energy + Sad Folk | Hollow Bones wins even though its energy (0.30) is opposite to what was requested (0.92) — genre+mood labels dominate |
| 5 | ADVERSARIAL: Metal (not in catalog) | No genre match ever fires; system falls back gracefully to mood+energy signals |

### Weight-shift experiment

The weights were changed from `genre=2.0, energy=1.5` to `genre=1.0, energy=3.0`
(genre halved, energy doubled). Key findings:

- Top-1 results stayed the same for all three standard profiles — the correct song still won.
- The **gap between ranks shrank**. Rooftop Lights (indie pop + happy) went from 2.86 to 4.22
  — nearly catching Gym Hero (pop + intense) at 4.23. With original weights, Gym Hero's genre
  match (2.0) gave it a 1-point cushion; with halved genre weight, a mood match and strong
  energy match are nearly as valuable.
- For the lofi profile, **rankings were unchanged** — because lofi songs are also naturally
  low-energy, both the genre and energy signals point to the same songs.
- **Conclusion**: Doubling energy made the leaderboard more competitive and introduced more
  diversity in ranks 2–5, but did not change which song ranked first for any profile.
  The experiment suggests the original weights produce stable top-1 results but may
  over-reward genre matches in the lower ranks.

### Surprise finding

"Gym Hero" (pop, intense, energy 0.93) ranks #2 for the High-Energy Pop fan even though
its mood is "intense," not "happy." The reason: its genre match (+2.0) outweighs the
missing mood match (+0) compared to Rooftop Lights, which matched the mood (+1.0) but
is "indie pop" not "pop" so it gets no genre bonus. From a non-programmer's perspective:
the system thinks Gym Hero is a better "pop song" recommendation than Rooftop Lights
because it checks the genre box, even if the vibe is a workout song, not a happy anthem.
This is a good example of where mathematical rules can diverge from human intuition.

---

## 8. Future Work

- **Widen mood into a similarity spectrum.** Rather than exact string matching, a mood
  distance table (e.g., "relaxed" is 0.5 away from "chill", 1.0 away from "intense") would
  give partial credit and eliminate the binary cliff.
- **Add a diversity penalty.** If the top 3 results are all the same genre, reduce the score
  of the 3rd by a small amount to surface variety.
- **Use danceability as a scoreable feature** with a user preference toggle ("I want to dance").
- **Allow multi-genre profiles.** Real listeners like more than one genre. The profile could
  store a ranked list of preferred genres with decreasing bonuses.
- **Learn from skips.** If a user skips the top result, temporarily lower the weight on
  whatever feature that song matched best. This is a simple form of feedback learning.

---

## 9. Personal Reflection

### Biggest learning moment

The adversarial test was the turning point. I designed a user who wanted "folk, sad, and
high-energy (0.92)" — a deliberately conflicting profile — and the system confidently
returned Hollow Bones as the top result. Hollow Bones is a soft, quiet acoustic track with
energy 0.30. It is the opposite of high-energy. But it matched the genre and mood labels,
so it won 4.51 points out of 5.5 while better-fitting energetic songs sat far below.

That moment made something real: **the algorithm does not hear music, it reads labels.**
It has no idea that "folk" can mean both a gentle acoustic ballad and a hard-driving fiddle
reel. The system was not broken — it was doing exactly what the weights told it to do. The
bug was in my assumption that genre labels carry more information than they actually do.

### How AI tools helped — and where I had to double-check

AI tools (Copilot and Claude) helped at every scaffolding step: generating initial CSV rows
in the right format, explaining the difference between `sorted()` and `.sort()`, and
suggesting the `1 - |difference|` formula for closeness scoring. That last one was
particularly useful — without the prompt "how do I reward closeness rather than just higher
values?", I might have written something like `score += song.energy` which rewards high
energy unconditionally and would have broken the chill-listener profile.

Where I had to slow down and verify: the AI-suggested scoring formula looked correct but I
had to manually trace through two contrasting songs (Library Rain vs. Storm Runner) to
confirm it produced the expected 5.42 vs. 1.27 output. AI tools are good at producing
plausible code — they are not good at knowing whether that code reflects what you actually
mean. Checking the math by hand on a known example was the only way to trust it.

### What surprised me about simple algorithms "feeling" like recommendations

What surprised me most is how believable the results look even though the logic is five
arithmetic operations. Run `python -m src.main` and the terminal prints a ranked list with
reasons — it genuinely looks like something a music app would show. The labels ("genre
match", "energy fit") create an impression of understanding that the code does not have.

This is worth taking seriously. A user reading "Midnight Coding recommended because: genre
match, chill mood, energy fit" might assume the system listened to the song and judged its
vibe. It did not. It compared three stored numbers and one string. The gap between
"looks like intelligence" and "is intelligence" is much smaller than I expected when the
output is formatted well — which is exactly why model cards and explanation text matter.

### What I would try next

If I kept developing this, the first change would be replacing exact mood matching with a
mood similarity table. "Relaxed" and "chill" are not the same string, but they are close in
meaning — a two-point penalty for treating them as completely different is too harsh. The
second change would be adding one "surprise" slot to the top-5: always include one song
that scores highly on energy and valence but does not match the genre, to push against the
filter bubble. The third would be logging which songs a user skips, and using that to
lower the weight of whichever feature those songs matched best — the simplest possible form
of feedback learning that does not require a real database or user accounts.
