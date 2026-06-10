# User Profile Design

## Goal

The user profile stores long-term travel preferences inferred from saved recommendations.

The profile is updated only when the user clicks "Save".

## Authentication

Users log in with an email address and password.

The database must never store plain-text passwords. It should store only a password hash and the required salt or hash metadata.

Email addresses should be normalized before saving:

- trim leading and trailing whitespace
- convert to lowercase

The first version only needs lightweight local authentication for the Gradio prototype. It does not need full production features such as password reset, email verification, session expiry, or OAuth.

## Profile Fields

| Field | Meaning |
|---|---|
| beach | User likes beaches, sea, islands, coastal cities |
| nature | User likes nature, lakes, mountains, forests |
| outdoor | User likes outdoor activities such as hiking, cycling, skiing |
| historic | User likes history, castles, old towns, museums |
| culture | User likes art, architecture, galleries, local culture |
| nightlife | User likes bars, clubs, concerts, parties |
| food | User likes restaurants, cafes, wine, local cuisine |
| shopping | User likes shopping, markets, fashion |
| low_cost | User prefers cheaper destinations |
| low_carbon | User prefers lower-carbon travel |
| dry_weather | User prefers dry weather or low rain risk |

## Data Format

Each field is stored as an integer score.

Example:

```json
{
  "beach": 2,
  "nature": 5,
  "outdoor": 4,
  "historic": 1,
  "culture": 2,
  "nightlife": 0,
  "food": 3,
  "shopping": 0,
  "low_cost": 4,
  "low_carbon": 3,
  "dry_weather": 1
}
```

## Update Rule

When the user saves a recommendation, extract preferences from:

- query
- starting_point
- cost_preference
- weather
- carbon_footprint_preference
- recommendation result

Then increase matching profile scores.

Example query:

```text
I like beaches, nightlife and cheap cities.
```

Example update:

```json
{
  "beach": 1,
  "nightlife": 1,
  "low_cost": 1
}
```

## Important Rule

The current user query has higher priority than the long-term profile.

The profile should only be used as a soft preference.
