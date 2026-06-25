#!/usr/bin/env python3
"""One-off optimizer for data/questions_About_MC_Test.json and LO markdown."""

from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
JSON_PATH = ROOT / "data" / "questions_About_MC_Test.json"
LO_PATH = ROOT / "data" / "questions_About_MC_Test_Learning_Objectives.md"

LEGACY_KEYS = {
    "frage",
    "optionen",
    "loesung",
    "erklaerung",
    "gewichtung",
    "thema",
    "kognitive_stufe",
}

LO_MARKDOWN = """# Overarching Learning Objectives: About MC Test: Understanding the EDULEARN26 Paper

## Formative Assessment and Cognitive Transparency
**Learners can explain MC Test as a formative practice platform with an explicit three-level cognitive model.**

This cluster covers the core purpose of MC Test and its Bloom-inspired taxonomy of reproduction, application, and analysis. It explains why the system goes beyond total scores and why cognitive demand is modeled directly in each item.

---

## Learner-Facing Analytics for Study Planning
**Learners can use MC Test dashboards to diagnose performance by topic, concept, and cognitive level.**

This cluster connects the Cognitive Radar Chart, Topic × Cognitive Heatmap, Topic Performance Chart, and Concept Mastery Columns. It shows how learners move from a single score to more specific study targets.

---

## Concept Mastery, Feedback, and Vocabulary Support
**Learners can interpret concept-level results together with item explanations and mini-glossaries.**

This cluster links feedback, concept mastery, and vocabulary support. It focuses on the 70% concept-mastery heuristic from the paper and on reading item-level and concept-level evidence carefully without overclaiming beyond the available data.

---

## LLM-Assisted Item Generation and Quality Assurance
**Learners can describe MC Test item generation as a controlled workflow rather than free-form automated authoring.**

This cluster covers finite-state prompting, schema-driven output, automated validation, repair, option harmonization, and instructor review. LLM support improves authoring workflows, but it does not remove quality assurance.

---

## Adaptive Pacing and Rapid-Guessing Mitigation
**Learners can interpret pacing mechanisms as configurable nudges for reading, reflection, and completion.**

This cluster addresses Pre-Answer Cooldown, Post-Answer Cooldown, Time-Critical Override, and response-time evidence. Pacing is treated as a design hypothesis to be evaluated, not as proof of deeper learning.

---

## Privacy-Aware Architecture and Institutional Deployment
**Learners can identify architectural choices that support privacy-sensitive deployment in educational settings.**

This cluster includes on-premises LLM inference, pseudonymous access, local MathJax rendering, on-premises PostgreSQL persistence in the EDULEARN26 deployment, and reduced data transfer risk. It links technical implementation choices to institutional data sovereignty.

---

## Evaluation Evidence and Claim Boundaries
**Learners can judge MC Test evidence claims with appropriate methodological caution.**

This cluster focuses on usability evidence, cognitive-label reliability, rapid-guessing evaluation, and future learning-outcome validation. It helps learners separate implemented design features from empirically established effects.

---

# Detailed Learning Objectives

In the context of **About MC Test: Understanding the EDULEARN26 Paper**, this question set helps you achieve the following detailed learning objectives:

### Reproduction

**You can ...**

1. state the primary formative purpose of MC Test.
2. name the three cognitive levels used in the MC Test weighting model.
3. identify Streamlit as the application framework for MC Test.
4. name the three concept statuses shown in Concept Mastery Columns.
5. explain why an on-premises local LLM backend reduces institutional data transfer risk.

### Application

**You can ...**

1. explain why MC Test limits operational item labels to Bloom levels 1–3.
2. classify a ten-item concept result using the default 70% mastery heuristic from the EDULEARN26 paper.
3. select the Cognitive Radar Chart for cognitive-level performance profiles.
4. select the Topic × Cognitive Heatmap for topic-by-level performance patterns.
5. distinguish broad topics from fine-grained concepts in MC Test analytics.
6. interpret unanswered items as evidence for remediation or avoidance patterns.
7. explain how linking results to topics, concepts, cognitive levels, and explanations supports targeted study advice.
8. describe the Time-Critical Override under critical time pressure.
9. describe the mini-glossary as item-level vocabulary support.
10. explain why explicit confirmation is used in finite-state item generation.
11. select schema-driven validation with repair for malformed LLM item output.
12. identify option harmonization as a cue-reduction step for generated items.
13. explain why instructor review remains necessary after LLM-assisted generation.
14. describe pseudonymous access as a privacy-aware participation mechanism.
15. select local MathJax rendering for privacy-compliant notation display.
16. identify PostgreSQL as the persistence layer in the on-premises architecture described in the EDULEARN26 paper.
17. select Cohen's kappa for cognitive-label reliability checks.
18. interpret a mean SUS score as preliminary perceived-usability evidence.
19. select system logs with response times for rapid-guessing evaluation.

### Analysis

**You can ...**

1. diagnose a broad process-level analysis difficulty across topic patterns.
2. evaluate the MC Test quality-assurance chain for LLM-generated items.
3. assess semantic validation for syntactically valid JSON with difficulty-profile drift.
4. analyze how post-answer cooldown and extended feedback support reflection after fast incorrect responses.
5. assess the current evidence boundaries for usability, rapid guessing, and learning outcomes in MC Test.
"""


def _strip_legacy(question: dict) -> dict:
    return {k: v for k, v in question.items() if k not in LEGACY_KEYS}


def _apply_text_patches(questions: list[dict]) -> None:
    """Question stems and options are maintained directly in the JSON file."""
    return

def _global_text_cleanup(value):
    if isinstance(value, str):
        text = value.replace("MC-Test", "MC Test")
        text = re.sub(r"\bdata-transfer\b", "data transfer", text)
        return text
    if isinstance(value, list):
        return [_global_text_cleanup(v) for v in value]
    if isinstance(value, dict):
        return {k: _global_text_cleanup(v) for k, v in value.items()}
    return value


def main() -> None:
    with JSON_PATH.open(encoding="utf-8") as handle:
        payload = json.load(handle)

    questions = [_strip_legacy(q) for q in payload["questions"]]
    _apply_text_patches(questions)
    questions = _global_text_cleanup(questions)

    weights = {1: 0, 2: 0, 3: 0}
    for q in questions:
        weights[int(q["weight"])] += 1

    minutes = round(weights[1] * 0.5 + weights[2] * 0.75 + weights[3] * 1.0 + 5)
    if minutes >= 10:
        minutes = ((minutes + 4) // 5) * 5

    meta = {
        "title": "About MC Test: Understanding the EDULEARN26 Paper",
        "created": payload.get("meta", {}).get("created", "25.06.2026 13:40"),
        "updated": "2026-06-25",
        "language": "en",
        "target_audience": "Participants in the EDULEARN26 session on student performance and predictive analytics",
        "question_count": len(questions),
        "difficulty_profile": {
            "easy": weights[1],
            "medium": weights[2],
            "hard": weights[3],
        },
        "time_per_weight_minutes": {"1": 0.5, "2": 0.75, "3": 1.0},
        "additional_buffer_minutes": 5,
        "test_duration_minutes": minutes,
    }

    cleaned = {"meta": meta, "questions": questions}
    cleaned = _global_text_cleanup(cleaned)

    with JSON_PATH.open("w", encoding="utf-8") as handle:
        json.dump(cleaned, handle, ensure_ascii=False, indent=2)
        handle.write("\n")

    LO_PATH.write_text(LO_MARKDOWN, encoding="utf-8")
    print(f"Wrote {JSON_PATH.name} and {LO_PATH.name}")


if __name__ == "__main__":
    main()
