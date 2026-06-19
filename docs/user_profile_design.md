# User Profile Design

## Goal

The user profile stores long-term travel preferences inferred from recommendations that the user explicitly saves.

The current search query always has priority. The long-term profile is a soft preference when a current query exists, and becomes the main recommendation source only when the query is empty.

## Authentication

Users log in with an email address and password. Passwords are stored only as salted password hashes, never as plain text.

Email addresses are normalized by trimming whitespace and converting them to lowercase.

## Preference Taxonomy

### Interests

| Tag | Meaning |
|---|---|
| `beach_coast` | Beaches, islands, coastal destinations and sunbathing |
| `mountains_hiking` | Mountains, trails, hiking, trekking and climbing |
| `nature_wildlife` | Forests, lakes, national parks, scenery and wildlife |
| `winter_sports` | Skiing, snowboarding and other snow activities |
| `water_sports` | Swimming, surfing, diving, kayaking and sailing |
| `history_heritage` | Historic places, castles, old towns, ruins and heritage |
| `arts_museums` | Museums, galleries, exhibitions and visual arts |
| `architecture` | Architecture, cathedrals, churches and notable buildings |
| `local_culture` | Traditions, folklore, local communities and authentic experiences |
| `food_drink` | Restaurants, local cuisine, wine, beer and gastronomy |
| `nightlife` | Bars, clubs and parties |
| `music_festivals` | Concerts, live music and festivals |
| `shopping_markets` | Shopping, local markets, boutiques and fashion |
| `wellness_relaxation` | Spas, thermal baths, retreats and relaxing trips |

### Destination Style

| Tag | Meaning |
|---|---|
| `major_city` | Large cities, metropolitan experiences and city breaks |
| `small_town` | Small towns, villages, countryside and quiet destinations |
| `hidden_gems` | Less crowded, offbeat and non-touristy destinations |

### Budget, Climate and Sustainability

| Tag | Meaning |
|---|---|
| `budget` | Affordable and low-cost travel |
| `luxury` | Premium, high-end and luxury travel |
| `dry_weather` | Preference for sunny or low-rain conditions |
| `low_carbon` | Preference for low-emission and sustainable transport |

Solo, couple and family travel are treated as current-trip context. They are not stored as long-term profile preferences.

## Storage Model

Preferences are stored in a normalized SQLite table so new tags can be introduced without adding database columns.

```sql
CREATE TABLE user_profile_preferences (
    user_id INTEGER NOT NULL,
    tag TEXT NOT NULL,
    score REAL NOT NULL DEFAULT 0,
    updated_at TEXT NOT NULL,
    PRIMARY KEY (user_id, tag),
    FOREIGN KEY (user_id) REFERENCES users(id)
);
```

Example data:

```text
user_id | tag                 | score
1       | mountains_hiking    | 3.40
1       | history_heritage    | 1.60
1       | budget              | 2.44
```

## Profile Update Rule

The profile is updated only when the user saves a recommendation.

Preferences are extracted from:

- the current query
- cost, weather and carbon settings
- the generated recommendation

Before adding the newly detected preferences, every existing score is decayed:

```text
new_score = old_score * 0.8 + current_preference_score
```

Example:

```text
Old beach_coast score: 5.0
No new beach preference: 5.0 * 0.8 + 0 = 4.0

Old mountains_hiking score: 3.0
New hiking preference: 3.0 * 0.8 + 1 = 3.4
```

This gives more weight to recent saved preferences while retaining useful long-term history.

## Recommendation Rule

- If the user enters a query, the query has priority and the profile is a soft preference.
- If the query is empty, active profile tags are converted into the retrieval query.
- Zero-score tags are ignored when building recommendations.
