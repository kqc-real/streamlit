#!/usr/bin/env python3
"""Print cooldowns per weight + tempo using current AppConfig normalization."""
from config import AppConfig

def compute_cooldowns(per_weight_minutes, normalization):
    tempos = {
        'normal': 1.0,
        'speed': 0.5,
        'power': 0.25,
    }
    variants = [
        ('no_explanation', 0),
        ('explanation', 10),
        ('extended', 20),
        ('both', 30),
    ]

    rows = []
    for weight in sorted(per_weight_minutes.keys()):
        base_minutes = per_weight_minutes[weight]
        base_seconds = round(base_minutes * 60)
        for tempo_code, tempo_mult in tempos.items():
            next_base = int(round(base_seconds * tempo_mult))
            for name, extra in variants:
                total = int(round((next_base + extra) * normalization))
                rows.append((weight, tempo_code, name, next_base, extra, normalization, total))
    return rows


def print_table(rows):
    last_weight = None
    for w, tempo, name, next_base, extra, norm, total in rows:
        if w != last_weight:
            print(f"\nWeight {w} (base next_base depends on tempo)")
            print("Tempo    | variant       | next_base | extra | norm  | total_seconds")
            print("-------- | ------------- | ---------:| -----:| -----:| -------------:")
            last_weight = w
        print(f"{tempo:7} | {name:13} | {next_base:9d} | {extra:5d} | {norm:5.2f} | {total:13d}")


if __name__ == '__main__':
    cfg = AppConfig()
    norm = getattr(cfg, 'next_cooldown_normalization_factor', 1.0) or 1.0
    # default per-weight minutes used by the app unless set in question meta
    per_weight_minutes = {1: 0.5, 2: 0.75, 3: 1.0}
    print(f"Using normalization factor from AppConfig: {norm}\n")
    rows = compute_cooldowns(per_weight_minutes, norm)
    print_table(rows)
