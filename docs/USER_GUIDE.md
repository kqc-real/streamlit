# User Guide

## Overview
- Web-based MC test app with localization (dates, numbers, UI labels).
- Supports pacing timers, panic mode, skipping, bookmarking, and review flows.
- Results view with topic performance, cognitive stages, exports, and admin tools (if enabled).

## Start a Test
1) Open the app and choose language via the locale selector (top bar).
2) Pick a question set (built-in or uploaded), then click **Start test**.
3) The timer starts; pacing helper shows remaining time vs. question count.

## Answering Questions
- Choose an option; **Submit answer** turns highlighted once a choice is made.
- **Skip** moves the question to the skipped queue (reappears later).
- **Bookmark** keeps a question in the bookmarked list for quick jumps.
- Cooldowns guide pacing; in **panic mode** (time-critical) cooldowns are disabled and Skip/Submit stay active.

## Navigation
- Normal flow: **Next/Summary** appears after answering.
- Skip review (jumped to a skipped question): controls show **Back to current question** and **Next skipped question** (if any); generic Prev/Next are hidden.
- Bookmark review (jumped to a bookmarked question): **Previous/Next bookmarked question** (if neighbors) and **Back to current question**; generic Prev/Next are hidden.
- Panic mode still allows Next/Summary after answering.

## Results & Exports
- After the last answer (or time expiry), see the summary: score, topic performance (localized legend/hover), cognitive stages, and per-question review.
- Exports: glossary, PDF solution, CSV (if enabled in your deployment).
- Animations (balloons/snow) appear on high-weight correct answers and on perfect scores.

## Admin (if enabled)
- Admin panel in the sidebar (secured by admin key unless in local/dev).
- Actions: audit log, user/session management, test data cleanup, solution/exports regeneration.

## Tips & Troubleshooting
- If you jump to a question and controls vanish, use **Back to current question** in the review flow.
- In panic mode, both Skip and Submit remain clickable; cooldown hints are suppressed.
- Skipped queue order is preserved; “Next skipped question” walks the queue.
- Localization: dates/times/numbers use your selected locale; charts and legends are translated.
