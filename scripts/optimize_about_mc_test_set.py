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
7. use dashboard metadata to guide targeted study decisions.
8. describe the Pre-Answer Cooldown as reading support against rapid guessing.
9. describe the Time-Critical Override under critical time pressure.
10. describe the mini-glossary as item-level vocabulary support.
11. explain why explicit confirmation is used in finite-state item generation.
12. select schema-driven validation with repair for malformed LLM item output.
13. identify option harmonization as a cue-reduction step for generated items.
14. explain why instructor review remains necessary after LLM-assisted generation.
15. describe pseudonymous access as a privacy-aware participation mechanism.
16. select local MathJax rendering for privacy-compliant notation display.
17. identify PostgreSQL as the persistence layer in the on-premises architecture described in the EDULEARN26 paper.
18. select Cohen's kappa for cognitive-label reliability checks.
19. interpret a mean SUS score as preliminary perceived-usability evidence.
20. select system logs with response times for rapid-guessing evaluation.

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
    patches: dict[int, dict] = {
        1: {
            "question": "1. What is the primary purpose of MC Test?",
            "options": [
                "To deliver high-stakes summative exams at institutional scale",
                "To support formative MC practice with feedback and analytics",
                "To replace instructor review in multiple-choice assessment workflows",
                "To serve as a generic course-evaluation or opinion survey tool",
            ],
            "explanation": "MC Test is built for formative multiple-choice practice, not to replace instructors. Its core value is linking practice items to feedback, learner-facing analytics, and pacing.",
        },
        2: {
            "question": "2. Which three cognitive levels does MC Test use for item weights?",
            "explanation": "MC Test uses a restricted three-level taxonomy inspired by Bloom: reproduction, application, and analysis.",
        },
        3: {
            "question": "3. Which framework is used to build the MC Test web application?",
            "options": [
                "Static HTML pages without interactive backend logic",
                "Moodle as the sole application and hosting layer",
                "Streamlit as the Python web application framework",
                "A spreadsheet-based macro authoring system",
            ],
            "explanation": "MC Test is implemented as a Streamlit web application. That choice supports rapid development of interactive Python-based learning tools.",
        },
        4: {
            "question": "4. What three statuses does the Concept Mastery Columns view use?",
            "options": [
                "Fast, medium, and slow response pacing bands",
                "Public, private, and anonymous access classifications",
                "Easy, medium, and hard item difficulty tiers",
                "Understood, not attempted, and not understood",
            ],
            "explanation": "Concept Mastery Columns group fine-grained concepts by learner performance. The three statuses are understood, not attempted, and not understood.",
        },
        5: {
            "question": "5. Which deployment goal best motivates an on-premises local LLM backend in MC Test?",
            "options": [
                "Removing the need for instructor review",
                "Guaranteeing perfect item quality",
                "Reducing institutional data transfer risk",
                "Hiding learner analytics from students",
                "Eliminating the need for validation",
            ],
            "explanation": "A local backend supports privacy-sensitive deployment by keeping prompts and learner data inside institutional infrastructure. It does not remove validation or instructor review.",
        },
        6: {
            "question": "6. A learner scores well on reproduction items but poorly on application and analysis. Which MC Test view best reveals this cognitive profile?",
            "explanation": "The Cognitive Radar Chart summarizes performance across reproduction, application, and analysis. It shows whether a learner mainly recalls facts or can also apply and analyze ideas.",
        },
        7: {
            "question": "7. An instructor wants to generate multiple-choice items with an LLM without importing malformed output. Which MC Test design choice addresses this most directly?",
            "options": [
                "Longer answer explanations attached to each answer option",
                "A lower default threshold for concept mastery rules",
                "Schema-driven JSON output with validation and repair",
                "A larger catalog of unanswered response category labels",
            ],
            "explanation": "Schema-driven JSON output makes generated items machine-checkable. Validation and repair loops catch structural problems before import and review.",
            "extended_explanation": {
                "title": "Why schema constraints matter",
                "content": "LLM output should not be treated as valid by default. MC Test therefore treats generation as a controlled pipeline in which parseability, field completeness, and answer-index validity are checked explicitly.",
                "steps": [
                    "Recognize that malformed output is a structural problem.",
                    "Use a schema to define the required item format.",
                    "Apply validation to detect errors.",
                    "Use a repair loop for minimal correction before human review.",
                ],
            },
        },
        8: {
            "topic": "LLM Item Generation",
            "question": "8. A generated item makes the correct option obvious because it is much longer than the distractors. Which MC Test mechanism is intended to reduce this cueing problem?",
            "explanation": "Option harmonization revises answer choices so the keyed option is not obvious from length, syntax, or specificity. It preserves the answer key while improving item quality.",
        },
        9: {
            "question": "9. A learner skips most analysis items in one topic but answers reproduction items in that topic correctly. Which dashboard view best separates this topic-level and cognitive-level pattern?",
            "options": [
                "Concept Mastery Columns dashboard view",
                "Topic × Cognitive Heatmap dashboard view",
                "Single total score summary display",
                "Item-level mini-glossary reference panel",
            ],
            "explanation": "The Topic × Cognitive Heatmap crosses topics with cognitive levels. It helps show whether a difficulty is tied to one topic, one cognitive level, or their combination.",
        },
        10: {
            "question": "10. Why does MC Test limit operational item labels to Bloom levels 1–3?",
            "options": [
                "Because dashboards cannot display more than three colors",
                "Because higher-order generation and validation are harder to keep reliable",
                "Because learners should focus mainly on memorizing facts in STEM courses",
                "Because formative assessment cannot use cognitive taxonomies",
            ],
            "explanation": "MC Test focuses on Bloom-inspired levels 1–3 to improve verifiability and reduce semantic risk. Evaluation and creation tasks are harder to generate and validate reliably in closed multiple-choice formats.",
            "extended_explanation": {
                "title": "Rationale for restricting levels",
                "content": "The restriction is a pragmatic design choice. It keeps the item model operational and lowers risk while still covering recall, transfer, and analytical reasoning.",
                "steps": [
                    "Recognize that MC Test targets closed multiple-choice items.",
                    "Link closed formats to constraints on what can be assessed reliably.",
                    "Prefer levels that can be reviewed and validated more consistently.",
                    "Retain human review because restriction alone does not guarantee quality.",
                ],
            },
        },
        11: {
            "question": "11. In the MC Test item-generation workflow, why is explicit confirmation requested before final JSON output?",
            "options": [
                "To confirm generation settings before final output",
                "To let the system skip validation after generation",
                "To remove the need for learning objectives",
                "To require every learner to author a question set",
                "To prevent instructors from changing topics later",
            ],
            "explanation": "The finite-state workflow collects parameters step by step. Explicit confirmation ensures that topic, audience, item count, difficulty profile, option format, and context are clear before output is generated.",
        },
        12: {
            "question": "12. A course team wants learners to receive targeted study advice instead of only a score. Which MC Test design principle best supports this goal?",
            "options": [
                "To hide unanswered items completely on the learner dashboard",
                "To disable all feedback until the course has fully ended",
                "To report learner results only as one final percentage",
                "To link results to topics, concepts, levels, and explanations",
            ],
            "explanation": "MC Test is designed to move beyond a single total score. It links results to topics, concepts, cognitive levels, explanations, and study resources.",
            "extended_explanation": {
                "title": "From score reporting to guidance",
                "content": "The formative value of MC Test lies in diagnostic detail. Learners can see not only whether they were wrong, but also what kind of knowledge or reasoning needs work.",
                "steps": [
                    "Recognize that a single score is too coarse for targeted learning.",
                    "Break performance down by topic and cognitive level.",
                    "Use explanations and glossaries to support remediation.",
                    "Turn patterns into concrete study targets.",
                ],
            },
        },
        13: {
            "question": "13. Which situation best illustrates the purpose of the Pre-Answer Cooldown?",
            "options": [
                "The learner must wait briefly before submitting an answer",
                "The instructor cannot review any generated item drafts",
                "The system deletes all old responses after the test ends",
                "The dashboard hides incorrect answers from the learner",
            ],
            "explanation": "The Pre-Answer Cooldown disables the Submit button for a short item-specific time. It is meant as reading support and a nudge against impulsive rapid guessing.",
        },
        14: {
            "question": "14. What is the main purpose of the Time-Critical Override?",
            "options": [
                "To block learners with accommodations from finishing attempts",
                "To replace learner analytics with instructor-only reports",
                "To disable cooldowns when time per remaining item is critical",
                "To increase the scoring weight of unanswered items",
                "To remove pacing mechanisms permanently from a course",
            ],
            "explanation": "The Time-Critical Override relaxes cooldowns under strong time pressure. It prioritizes completion when fixed pacing would otherwise become a disadvantage.",
        },
        15: {
            "question": "15. A concept has 10 associated items, and the learner answered all 10 with 7 correct. Under the default MC Test mastery rule described in the EDULEARN26 paper, how is the concept classified?",
            "options": [
                "Classified as understood for the concept",
                "Classified as not attempted for the concept",
                "Classified as not understood for the concept",
                "Excluded entirely from concept analytics",
            ],
            "explanation": "The EDULEARN26 paper uses a 70% default heuristic: a concept counts as understood when at least 70% of its items are correct. Seven correct out of ten meets that threshold.",
            "extended_explanation": {
                "title": "Applying the mastery rule",
                "content": "The 70% rule in the paper is a configurable heuristic for study planning. It should not be interpreted as a psychometrically validated mastery cut score.",
                "steps": [
                    "Count the number of correct answers for the concept.",
                    "Divide correct answers by the relevant item total.",
                    "Compare the result with the 70% threshold.",
                    "Classify the concept as understood when the threshold is met.",
                ],
            },
        },
        16: {
            "topic": "Formative Assessment",
            "question": "16. Why does MC Test include a mini-glossary for individual items?",
            "options": [
                "To store personally identifiable learner profile data",
                "To rank learners publicly by terminology knowledge",
                "To replace answer explanations with glossary entries",
                "To provide vocabulary help at the point of feedback",
            ],
            "explanation": "The mini-glossary gives learners short definitions of terms that matter for the item. It supports understanding directly at the point of feedback.",
        },
        17: {
            "question": "17. Which pair best describes the difference between topics and concepts in MC Test analytics?",
            "options": [
                "Topics are learner names; concepts are test dates",
                "Topics are response times; concepts are cooldown durations",
                "Topics are broad units; concepts are fine-grained targets",
                "Topics are incorrect options; concepts are correct options",
                "Topics are privacy settings; concepts are database tables",
            ],
            "explanation": "MC Test uses topics as broader curriculum units and concepts as finer-grained learning targets. That distinction supports both overview-level and remediation-level analytics.",
            "extended_explanation": {
                "title": "Understanding analytics granularity",
                "content": "The topic-concept distinction helps learners move from general impressions to concrete remediation targets. It is central to the diagnostic funnel of MC Test.",
                "steps": [
                    "Use topics for broad performance patterns.",
                    "Use concepts for more specific diagnosis.",
                    "Combine both levels to guide study planning.",
                    "Avoid treating one concept as a complete topic.",
                ],
            },
        },
        18: {
            "question": "18. An instructor wants to know whether two reviewers assign the same cognitive-level labels to items. Which measure is appropriate for this purpose?",
            "options": [
                "Concept mastery percentage by topic area",
                "Mean System Usability Scale composite score",
                "Total database storage size in megabytes",
                "Cohen's kappa for inter-rater label agreement",
            ],
            "explanation": "Cohen's kappa is planned to assess agreement between double coders of cognitive-level labels. It helps show whether the labels are reliable enough to interpret.",
        },
        19: {
            "question": "19. What does a mean SUS score of 70.38 primarily indicate in the MC Test evaluation context?",
            "options": [
                "Perfect reliability of cognitive-level item labels",
                "Validated reduction of rapid-guessing item behavior",
                "Preliminary evidence of acceptable perceived usability",
                "Definitive proof of measurable learner learning gains",
                "Complete elimination of all accessibility concerns",
            ],
            "explanation": "The SUS result provides preliminary evidence about perceived usability. It does not establish learning gains, reduced rapid guessing, or label reliability.",
        },
        20: {
            "question": "20. Why is human instructor review still necessary after LLM-assisted item generation in MC Test?",
            "options": [
                "Because validation alone cannot ensure educational quality",
                "Because generated explanations cannot be learner-facing",
                "Because JSON output makes instructor review impossible",
                "Because local LLMs cannot produce any structured text",
            ],
            "explanation": "Validation can check structure and some semantic constraints, but it cannot guarantee full educational quality. Human review remains necessary for correctness, alignment, and item quality.",
            "extended_explanation": {
                "title": "Limits of automation",
                "content": "The MC Test workflow improves robustness but does not remove expert responsibility. Educational assessment still needs both technical validation and domain-informed judgment.",
                "steps": [
                    "Use the LLM to generate draft items.",
                    "Validate the generated structure automatically.",
                    "Repair formal errors when possible.",
                    "Let instructors review content, alignment, and educational quality.",
                ],
            },
        },
        21: {
            "question": "21. A learner sees many unanswered items and a low percentage correct in one topic. Which interpretation is most appropriate?",
            "options": [
                "The topic may need remediation, and unanswered items matter",
                "The learner has mastered the topic because skipped items are neutral",
                "The dashboard is useless because unanswered items are included",
                "The learner clearly lacks all knowledge in that topic",
            ],
            "explanation": "Unanswered items may indicate avoidance or time-management issues. The low score should be read together with answered and total counts.",
        },
        22: {
            "question": "22. Which design choice best supports pseudonymous participation in MC Test?",
            "options": [
                "Publishing individual learner performance dashboards publicly",
                "Sending generation prompts to external social platforms",
                "Supporting progress tracking without personal accounts",
                "Requiring public learner profiles for every session",
                "Replacing session timestamps with learner full names",
            ],
            "explanation": "Pseudonymous participation supports progress tracking while reducing the need for personal accounts. That fits privacy-aware use in institutional teaching contexts.",
        },
        23: {
            "question": "23. Why does MC Test use local MathJax rendering instead of an external content delivery network?",
            "options": [
                "To prevent learners from seeing mathematical notation",
                "To reduce leakage of usage data to external hosts",
                "To make displayed formulas impossible for learners to copy",
                "To replace the need for any database persistence layer",
            ],
            "explanation": "Self-hosted MathJax helps avoid leaking usage data to external CDNs. That supports privacy-compliant rendering in institutional deployments.",
        },
        24: {
            "question": "24. In the on-premises architecture described in the EDULEARN26 paper, which database supports concurrent sessions and relational data?",
            "options": [
                "A browser cookie without persistent server-side storage",
                "PostgreSQL as the relational database persistence layer",
                "A spreadsheet exported manually after each practice session",
                "A slide deck embedded directly inside the application UI",
                "A single static JSON file used for all session data",
            ],
            "explanation": "The EDULEARN26 paper describes a Docker-based on-premises deployment that uses PostgreSQL for concurrent sessions and relational data such as user profiles, audit logs, and assessment records.",
        },
        25: {
            "question": "25. A course team wants to evaluate whether cooldowns reduce rapid guessing. Which data source is most relevant?",
            "options": [
                "The metadata title of the question set only",
                "The total number of mini-glossary terms only",
                "The learner's final percentage score summary only",
                "System logs of response times and learner behavior",
            ],
            "explanation": "Rapid guessing is inferred from response-time and behavior patterns. System logs are therefore more relevant than final scores alone.",
        },
        26: {
            "question": "26. A learner performs well in most topics but weakly on analysis across nearly all topics. What is the most defensible interpretation?",
            "options": [
                "The dashboard proves the analysis items are psychometrically invalid",
                "The learner should ignore all cognitive-level dashboard information",
                "The learner likely has a broad analysis gap rather than one topic gap",
                "The learner has no problem because overall topic scores remain strong",
            ],
            "explanation": "Weak analysis scores across topics suggest a pattern tied to cognitive demand, not just one topic. Still check evidence volume and item quality before drawing strong conclusions.",
        },
        27: {
            "question": "27. Which combination best represents the MC Test quality-assurance logic for LLM-generated items?",
            "options": [
                "Random generation, no metadata, and post-hoc score aggregation",
                "Free-form prompting, immediate publication, and learner ranking",
                "External API dependence, hidden prompts, and no repair strategy",
                "Schema-constrained generation, validation, harmonization, and review",
                "Single-score feedback, no explanations, and no cognitive labels",
            ],
            "explanation": "MC Test combines technical constraints with human review. The pipeline aims to produce parseable items, fix structural problems, reduce option cues, and preserve instructor control.",
            "extended_explanation": {
                "title": "Analyzing the QA chain",
                "content": "The logic is layered. No single mechanism guarantees high-quality items, so MC Test combines automated checks, targeted revisions, and human expertise.",
                "steps": [
                    "Start with constrained generation rather than free-form text.",
                    "Validate generated JSON for structure and answer-index correctness.",
                    "Repair structural or semantic drift where possible.",
                    "Harmonize options to reduce cueing.",
                    "Require instructor review before release.",
                ],
            },
        },
        28: {
            "question": "28. A local LLM backend produces syntactically valid JSON but sometimes changes the intended difficulty distribution. Which response best fits the MC Test design philosophy?",
            "options": [
                "Remove cognitive levels from the item model to simplify generation",
                "Accept the output because valid JSON is sufficient",
                "Add semantic validation for the requested difficulty profile",
                "Reject local models as unusable for education",
            ],
            "explanation": "Valid syntax alone is not enough. MC Test also needs semantic checks, such as whether generated weights match the requested difficulty profile.",
        },
        29: {
            "question": "29. A learner answers quickly and incorrectly, then wants to move on without reading the explanation. Which combination of MC Test mechanisms most directly addresses this behavior?",
            "options": [
                "Topic labels paired with public source-code release",
                "PostgreSQL storage paired with Docker Compose deployment",
                "Post-Answer Cooldown paired with extended feedback review",
                "Pseudonymous login paired with locally hosted MathJax",
                "SUS scoring paired with MIT open-source licensing",
            ],
            "explanation": "The Post-Answer Cooldown creates a short review window after submission. Extended feedback can support reflection by explaining the reasoning behind the item.",
        },
        30: {
            "question": "30. Which statement best captures the current evidence status of MC Test?",
            "options": [
                "It has proven large learning gains across STEM disciplines",
                "It offers design contribution with preliminary usability evidence",
                "It has eliminated the need for psychometric item analysis",
                "It is validated as a high-stakes examination platform",
            ],
            "explanation": "MC Test currently offers a system design contribution and preliminary perceived-usability evidence. Claims about learning outcomes, reduced rapid guessing, and cognitive-label reliability still need follow-up studies.",
            "extended_explanation": {
                "title": "Assessing claim strength",
                "content": "A rigorous reading separates what has been implemented from what has been empirically established. MC Test is promising, but its behavioral and learning effects still need systematic validation.",
                "steps": [
                    "Separate system design from outcome validation.",
                    "Treat usability evidence as preliminary.",
                    "Identify rapid guessing and learning gains as planned evaluation targets.",
                    "Avoid overstating what the current evidence supports.",
                ],
            },
        },
    }

    for idx, patch in patches.items():
        q = questions[idx - 1]
        q.update(patch)


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
        "test_duration_minutes": 30,
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
