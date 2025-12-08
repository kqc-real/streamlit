# Cooldown Table — per-weight / tempo / explanation extras

This file shows the computed cooldowns used by the UI for the "Antworten" / "Nächste Frage" flow.

Defaults used in the tables below:
- `time_per_weight_minutes`: {1: 0.5, 2: 0.75, 3: 1.0}
- Tempo multipliers: `normal = 1.0`, `speed = 0.5`, `power = 0.25`
- Extras: `explanation = +10s`, `extended_explanation = +20s`, `both = +30s`
- Normalization factor: scales the *entire cooldown* (base + extras) after tempo adjustment (default `1.0`).
- Base seconds are computed as `base_seconds = round(base_minutes * 60)` and then scaled by tempo and rounded.

Computation (per question):
1. Determine base minutes from `time_per_weight_minutes` for the question weight.
2. `base_seconds = round(base_minutes * 60)`
3. `next_base = round(base_seconds * tempo_multiplier)`
4. `extra = (10 if explanation) + (20 if extended_explanation)`
5. `total_next_cooldown = round((next_base + extra) * normalization_factor)`

---

## Table: Normalization factor = 1.0 (default)

Weight 1 (base 0.5 min = 30s)

| Tempo  | Base | No explanation | Explanation (+10) | Extended (+20) | Both (+30) |
|--------|------:|---------------:|------------------:|---------------:|-----------:|
| normal |  30s | 30s | 40s | 50s | 60s |
| speed  |  15s | 15s | 25s | 35s | 45s |
| power  |   8s |  8s | 18s | 28s | 38s |

Weight 2 (base 0.75 min = 45s)

| Tempo  | Base | No explanation | Explanation (+10) | Extended (+20) | Both (+30) |
|--------|------:|---------------:|------------------:|---------------:|-----------:|
| normal |  45s | 45s | 55s | 65s | 75s |
| speed  |  22s | 22s | 32s | 42s | 52s |
| power  |  11s | 11s | 21s | 31s | 41s |

Weight 3 (base 1.0 min = 60s)

| Tempo  | Base | No explanation | Explanation (+10) | Extended (+20) | Both (+30) |
|--------|------:|---------------:|------------------:|---------------:|-----------:|
| normal |  60s | 60s | 70s | 80s | 90s |
| speed  |  30s | 30s | 40s | 50s | 60s |
| power  |  15s | 15s | 25s | 35s | 45s |

---


## Table: Example normalization factor = 0.5 (scales whole cooldown)

Weight 1 (base 30s)

| Tempo  | Base | No explanation | Explanation (+10) | Extended (+20) | Both (+30) |
|--------|------:|---------------:|------------------:|---------------:|-----------:|
| normal |  30s | 15s | 20s | 25s | 30s |
| speed  |  15s | 8s  | 12s | 18s | 22s |
| power  |   8s | 4s  | 9s  | 14s | 19s |

Weight 2 (base 45s)

| Tempo  | Base | No explanation | Explanation (+10) | Extended (+20) | Both (+30) |
|--------|------:|---------------:|------------------:|---------------:|-----------:|
| normal |  45s | 22s | 28s | 32s | 38s |
| speed  |  22s | 11s | 16s | 21s | 26s |
| power  |  11s | 6s  | 10s | 16s | 20s |

Weight 3 (base 60s)

| Tempo  | Base | No explanation | Explanation (+10) | Extended (+20) | Both (+30) |
|--------|------:|---------------:|------------------:|---------------:|-----------:|
| normal |  60s | 30s | 35s | 40s | 45s |
| speed  |  30s | 15s | 20s | 25s | 30s |
| power  |  15s | 8s  | 12s | 18s | 22s |

---

If you want this as a CSV instead (or both), tell me and I'll add/update the file.

File path: `docs/cooldown_table.md`
