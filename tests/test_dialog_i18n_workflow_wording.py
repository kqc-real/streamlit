import json
from pathlib import Path


I18N_DIR = Path("i18n")

LLM_TERMS = {
    "de": ("externem LLM", "externen LLM", "externes LLM", "externe LLM"),
    "en": ("external LLM",),
    "es": ("LLM externo",),
    "fr": ("LLM externe",),
    "it": ("LLM esterno",),
    "zh": ("外部 LLM",),
}

ENTRYPOINT_KEYS = (
    ("sidebar", "create_user_qset"),
    ("welcome", "splash", "create_ai"),
    ("dialog", "title"),
)

WORKFLOW_KEYS = (
    "intro",
    "intro_info",
    "questionset_caption",
    "alternative_caption",
    "learning_objectives_caption",
    "postproduction_caption",
    "postproduction_set_for_ai_caption",
    "postproduction_lo_caption",
    "postproduction_lo_inputs_caption",
)

BANNED_FRAGMENTS = (
    "KI-Hilfe",
    "deiner KI",
    "an die KI",
    "QA-Postproduction",
    "QA des",
    "QA der",
    "Your set is public",
    "AI assistance",
    "your AI",
    "con IA",
    "avec IA",
    "con l’IA",
    "AI 用",
    "Kahoot",
    "arsnova.click",
    "Anki-Prompt",
)


def _nested_value(payload: dict, path: tuple[str, ...]) -> str:
    value = payload
    for key in path:
        value = value[key]
    assert isinstance(value, str)
    return value


def _contains_any(text: str, needles: tuple[str, ...]) -> bool:
    return any(needle in text for needle in needles)


def test_create_set_workflow_mentions_external_llm_in_all_languages():
    for path in sorted(I18N_DIR.glob("*.json")):
        language = path.stem
        payload = json.loads(path.read_text(encoding="utf-8"))
        terms = LLM_TERMS[language]

        for key_path in ENTRYPOINT_KEYS:
            text = _nested_value(payload, key_path)
            assert _contains_any(text, terms), f"{path}:{'.'.join(key_path)}"

        dialog = payload["dialog"]
        for key in WORKFLOW_KEYS:
            text = dialog[key]
            assert _contains_any(text, terms), f"{path}:dialog.{key}"


def test_create_set_workflow_keeps_json_markdown_transfer_clear():
    for path in sorted(I18N_DIR.glob("*.json")):
        dialog = json.loads(path.read_text(encoding="utf-8"))["dialog"]

        assert "JSON" in dialog["questionset_caption"]
        assert "JSON" in dialog["alternative_caption"]
        assert "Markdown" in dialog["learning_objectives_caption"]
        assert "Markdown" in dialog["learning_objectives_paste_caption"]
        assert "JSON" in dialog["postproduction_caption"]
        assert "JSON" in dialog["postproduction_paste_caption"]
        assert "Markdown" in dialog["postproduction_lo_caption"]
        assert "Markdown" in dialog["postproduction_lo_paste_caption"]


def test_create_set_workflow_copy_has_no_legacy_ai_or_export_wording():
    for path in sorted(I18N_DIR.glob("*.json")):
        payload = json.loads(path.read_text(encoding="utf-8"))
        relevant_text = json.dumps(
            {
                "sidebar": payload["sidebar"].get("create_user_qset", ""),
                "welcome_splash": payload["welcome"].get("splash", {}),
                "welcome": {
                    "create_own_set": payload["welcome"].get("create_own_set", ""),
                    "create_own_set_hint": payload["welcome"].get("create_own_set_hint", ""),
                    "empty_state": payload["welcome"].get("empty_state", ""),
                },
                "dialog": payload["dialog"],
            },
            ensure_ascii=False,
        )

        for fragment in BANNED_FRAGMENTS:
            assert fragment not in relevant_text, f"{path}: {fragment}"


def test_about_text_matches_edulearn_paper_core_claims():
    required_markers = ("MC-Test", "LLM", "Bloom", "Time-Critical Override", "Ollama", "SUS", "N=20")

    for path in sorted(I18N_DIR.glob("*.json")):
        payload = json.loads(path.read_text(encoding="utf-8"))
        text = payload["sidebar"]["about_project_text"]

        for marker in required_markers:
            assert marker in text, f"{path}: {marker}"
