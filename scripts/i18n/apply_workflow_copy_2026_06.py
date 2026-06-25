#!/usr/bin/env python3
"""One-off helper: optimized workflow UI copy for all locales."""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
I18N = ROOT / "i18n"

# Nested patches per locale. Keys omitted stay unchanged.
PATCHES: dict[str, dict] = {
    "de": {
        "sidebar": {
            "create_user_qset": "Fragenset mit externem LLM",
            "user_qset_dialog_warning": "Schließe zuerst den offenen Dialog.",
        },
        "welcome": {
            "splash": {
                "create_ai": "Fragenset mit externem LLM",
                "hero_subtitle": "Fertiges Set wählen – oder eigenes Set in vier Stufen mit externem LLM erstellen.",
            },
            "create_own_set": "🧠 Eigenes Fragenset",
            "create_own_set_hint": "Vier Stufen in einem externen LLM-Chat; hier speicherst du JSON und Markdown.",
            "empty_state": "Kein Fragenset aktiv. Wähle ein Set oder erstelle ein eigenes.",
        },
        "dialog": {
            "title": "✨ Fragenset mit externem LLM",
            "intro": (
                "Ein Chat mit deinem externen LLM (z. B. ChatGPT, Claude, Gemini) für **alle vier Stufen**. "
                "Hier speicherst du jedes Ergebnis:\n\n"
                "1) **Fragenset** – Prompt Stufe 1, Rückfragen beantworten, JSON speichern.\n"
                "2) **Lernziele** – Prompt Stufe 2 im **selben Chat**, Markdown speichern.\n"
                "3) **Fragenset prüfen** – Prompt Stufe 3 im **selben Chat**, JSON speichern.\n"
                "4) **Lernziele prüfen** – Prompt Stufe 4 im **selben Chat**, Markdown speichern."
            ),
            "intro_info": (
                "MC-Test erzeugt keine Inhalte. Ein Chat für alle Stufen: Prompts ins externe LLM kopieren, "
                "zurück nur **JSON oder Markdown** – ohne Zusatztext."
            ),
            "prompt_guide": "Der **MC-Test-Prompt** liefert das kanonische JSON für Tests, Anki und arsnova.eu.",
            "tab_selector_hint": "Tabs 1–4 = Stufen im externen LLM-Chat. Wähle, was du jetzt speichern willst.",
            "tab_selector_label": "Stufe (1–4)",
            "questionset_heading": "Stufe 1: Fragenset erzeugen",
            "questionset_caption": (
                "Neuen Chat mit deinem externen LLM öffnen, Prompt Stufe 1 einfügen, Rückfragen beantworten, "
                "JSON hier speichern. Stufen 2–4 im **selben Chat**."
            ),
            "prompt_expander_title": "Prompt Stufe 1",
            "upload_heading": "JSON speichern",
            "upload_warning": "⚠️ Max. 30 Fragen, max. 5 MB.",
            "upload_info": "Temporäre Sets: nach {hours} h gelöscht; mit reserviertem Pseudonym nach {days} Tagen.",
            "uploader_mode": "JSON hinzufügen",
            "uploader_help": "Max. 30 Fragen, 5 MB. Schema: MC-Test-JSON.",
            "alternative_heading": "### Oder: JSON einfügen",
            "alternative_caption": "Nur den JSON-Codeblock aus dem externen LLM einfügen – ohne Text davor oder danach.",
            "status_json_repair_hint": "Tipp: Fehlermeldung ins externe LLM kopieren – JSON lässt sich meist reparieren.",
            "status_error_hint": "Speichern fehlgeschlagen. Details anzeigen.",
            "lo_optional_info": "Optional: Lernziele in Stufe 2 speichern – oder ohne starten.",
            "learning_objectives_heading": "Stufe 2: Lernziele erzeugen",
            "learning_objectives_caption": (
                "Im **selben Chat mit deinem externen LLM**: Prompt Stufe 2 kopieren. JSON liegt im Verlauf. "
                "Nur Markdown hier speichern."
            ),
            "learning_objectives_hint_save_first": "Zuerst Stufe 1 abschließen und JSON speichern.",
            "learning_objectives_save_set_first": "Zuerst Stufe 1 abschließen und JSON speichern.",
            "learning_objectives_mode": "Lernziele hinzufügen",
            "learning_objectives_paste_caption": "Nur den Markdown-Codeblock einfügen.",
            "learning_objectives_help": "Dateiname wird automatisch zum Fragenset passend gesetzt.",
            "learning_objectives_prompt_expander": "Prompt Stufe 2",
            "learning_objectives_original_set_download": "⬇️ JSON (falls Chatverlauf fehlt)",
            "learning_objectives_save_success": "Lernziele gespeichert. Weiter mit Stufe 3 oder direkt starten.",
            "learning_objectives_set_loaded": "Aktiv: „{label}“",
            "questionset_save_success": "Fragenset gespeichert. Weiter mit Stufe 2.",
            "questionset_next_step": "Weiter: Stufe 2 – Lernziele erzeugen.",
            "postproduction_heading": "Stufe 3: Fragenset prüfen",
            "postproduction_caption": (
                "Im **selben Chat mit deinem externen LLM**: Prompt Stufe 3 kopieren. "
                "Nur bereinigtes JSON speichern."
            ),
            "postproduction_prompt_expander": "Prompt Stufe 3",
            "postproduction_set_for_ai_caption": (
                "Nur falls der Chatverlauf nicht reicht: dieses JSON im externen LLM verwenden."
            ),
            "postproduction_set_for_ai_download": "⬇️ JSON (falls Chatverlauf fehlt)",
            "postproduction_paste_caption": "Nur den bereinigten JSON-Codeblock einfügen.",
            "postproduction_save_success": "Geprüftes Fragenset gespeichert. Weiter mit Stufe 4.",
            "postproduction_lo_heading": "Stufe 4: Lernziele prüfen",
            "postproduction_lo_caption": (
                "Im **selben Chat mit deinem externen LLM**: Prompt Stufe 4 kopieren. "
                "Nur bereinigtes Markdown speichern."
            ),
            "postproduction_lo_prompt_expander": "Prompt Stufe 4",
            "postproduction_lo_inputs_caption": (
                "Nur falls der Chatverlauf nicht reicht: beide Dateien mit dem Prompt ans externe LLM senden."
            ),
            "postproduction_lo_set_download": "⬇️ Geprüftes JSON (falls nötig)",
            "postproduction_lo_download": "⬇️ Lernziele (falls nötig)",
            "postproduction_lo_paste_caption": "Nur den bereinigten Markdown-Codeblock einfügen.",
            "postproduction_lo_need_set": "Zuerst Stufe 3 abschließen.",
            "postproduction_lo_save_success": "Lernziele gespeichert. Du kannst starten.",
            "ai_bias_title": "Wozu Stufe 3 und 4?",
            "ai_bias_explanation": (
                "LLM-Ausgaben sind oft ungleichmäßig – z. B. längere Musterlösungen oder vage Lernziele. "
                "Stufe 3 und 4 glätten Fragenset und Lernziele vor dem Einsatz."
            ),
            "questionset_start_without_lo_warning": "⚠️ Ohne Lernziele starten – später in Stufe 2 nachholbar.",
            "questionset_start_without_lo_hint": "Lernziele kannst du jederzeit in Stufe 2 ergänzen.",
            "login_required": "Bitte anmelden, um zu starten.",
        },
        "user_qset": {
            "login_required": "Bitte anmelden, um zu starten.",
            "not_found": "Temporäres Fragenset nicht gefunden.",
            "no_questions": "Das Fragenset enthält keine Fragen.",
            "session_failed": "Start fehlgeschlagen.",
        },
    },
    "en": {
        "sidebar": {
            "create_user_qset": "Set with external LLM",
            "user_qset_dialog_warning": "Close the open dialog first.",
        },
        "welcome": {
            "splash": {
                "create_ai": "Set with external LLM",
                "hero_subtitle": "Pick a ready-made set – or build your own in four stages with an external LLM.",
            },
            "create_own_set": "🧠 Your own question set",
            "create_own_set_hint": "Four stages in one external LLM chat; save JSON and Markdown here.",
            "empty_state": "No active set. Pick one or create your own.",
        },
        "dialog": {
            "title": "✨ Question set with external LLM",
            "intro": (
                "Use **one chat** with your external LLM (e.g. ChatGPT, Claude, Gemini) for **all four stages**. "
                "Save each result here:\n\n"
                "1) **Question set** – Stage 1 prompt, answer follow-ups, save JSON.\n"
                "2) **Learning objectives** – Stage 2 prompt in the **same chat**, save Markdown.\n"
                "3) **Review set** – Stage 3 prompt in the **same chat**, save JSON.\n"
                "4) **Review objectives** – Stage 4 prompt in the **same chat**, save Markdown."
            ),
            "intro_info": (
                "MC Test does not generate content. One chat for all stages: copy prompts to your external LLM, "
                "paste back **only JSON or Markdown** – no extra text."
            ),
            "prompt_guide": "The **MC-Test prompt** produces canonical JSON for tests, Anki, and arsnova.eu.",
            "tab_selector_hint": "Tabs 1–4 match stages in your external LLM chat. Pick what you want to save now.",
            "tab_selector_label": "Stage (1–4)",
            "questionset_heading": "Stage 1: Generate question set",
            "questionset_caption": (
                "Open a new chat with your external LLM, paste the Stage 1 prompt, answer follow-ups, "
                "save JSON here. Stages 2–4 in the **same chat**."
            ),
            "prompt_expander_title": "Stage 1 prompt",
            "upload_heading": "Save JSON",
            "upload_warning": "⚠️ Max. 30 questions, 5 MB.",
            "upload_info": "Temporary sets: deleted after {hours} h; with a reserved pseudonym after {days} days.",
            "uploader_mode": "Add JSON",
            "uploader_help": "Max. 30 questions, 5 MB. Must match the MC-Test JSON schema.",
            "alternative_heading": "### Or: paste JSON",
            "alternative_caption": "Paste only the JSON code block from your external LLM – no text before or after.",
            "status_json_repair_hint": "Tip: paste the error into your external LLM – it can usually fix the JSON.",
            "status_error_hint": "Save failed. Show details.",
            "lo_optional_info": "Optional: save objectives in Stage 2 – or start without them.",
            "learning_objectives_heading": "Stage 2: Generate objectives",
            "learning_objectives_caption": (
                "In the **same chat with your external LLM**: copy the Stage 2 prompt. JSON is in the history. "
                "Save only Markdown here."
            ),
            "learning_objectives_hint_save_first": "Finish Stage 1 and save the JSON first.",
            "learning_objectives_save_set_first": "Finish Stage 1 and save the JSON first.",
            "learning_objectives_mode": "Add objectives",
            "learning_objectives_paste_caption": "Paste only the Markdown code block.",
            "learning_objectives_help": "The file name is matched to your set automatically.",
            "learning_objectives_prompt_expander": "Stage 2 prompt",
            "learning_objectives_original_set_download": "⬇️ JSON (if chat history is missing)",
            "learning_objectives_success": "Learning objectives saved as {filename}.",
            "learning_objectives_save_success": "Objectives saved. Continue to Stage 3 or start now.",
            "learning_objectives_set_loaded": "Active: “{label}”",
            "questionset_save_success": "Question set saved. Continue to Stage 2.",
            "questionset_next_step": "Next: Stage 2 – generate objectives.",
            "postproduction_heading": "Stage 3: Review question set",
            "postproduction_caption": (
                "In the **same chat with your external LLM**: copy the Stage 3 prompt. Save only cleaned JSON here."
            ),
            "postproduction_prompt_expander": "Stage 3 prompt",
            "postproduction_set_for_ai_caption": (
                "Only if chat history is not enough: use this JSON in your external LLM."
            ),
            "postproduction_set_for_ai_download": "⬇️ JSON (if chat history is missing)",
            "postproduction_paste_caption": "Paste only the cleaned JSON code block.",
            "postproduction_save_success": "Reviewed set saved. Continue to Stage 4.",
            "postproduction_lo_heading": "Stage 4: Review objectives",
            "postproduction_lo_caption": (
                "In the **same chat with your external LLM**: copy the Stage 4 prompt. Save only cleaned Markdown here."
            ),
            "postproduction_lo_prompt_expander": "Stage 4 prompt",
            "postproduction_lo_inputs_caption": (
                "Only if chat history is not enough: send both files with the prompt to your external LLM."
            ),
            "postproduction_lo_set_download": "⬇️ Reviewed JSON (if needed)",
            "postproduction_lo_download": "⬇️ Objectives (if needed)",
            "postproduction_lo_paste_caption": "Paste only the cleaned Markdown code block.",
            "postproduction_lo_need_set": "Finish Stage 3 first.",
            "postproduction_lo_save_success": "Objectives saved. You can start now.",
            "ai_bias_title": "Why stages 3 and 4?",
            "ai_bias_explanation": (
                "LLM output is often uneven – longer keyed options, weaker distractors, vague objectives. "
                "Stages 3 and 4 smooth the set and objectives before use."
            ),
            "questionset_start_without_lo_warning": "⚠️ Start without objectives – add them later in Stage 2.",
            "questionset_start_without_lo_hint": "You can add objectives anytime in Stage 2.",
            "login_required": "Please log in to start.",
        },
        "user_qset": {
            "login_required": "Please log in to start.",
            "not_found": "Temporary set not found.",
            "no_questions": "This set has no questions.",
            "session_failed": "Could not start.",
        },
    },
    "fr": {
        "sidebar": {"create_user_qset": "Jeu avec LLM externe"},
        "welcome": {
            "splash": {
                "create_ai": "Jeu avec LLM externe",
                "hero_subtitle": "Choisis un jeu prêt à l’emploi – ou crée le tien en quatre étapes avec un LLM externe.",
            },
            "create_own_set": "🧠 Ton propre jeu",
            "create_own_set_hint": "Quatre étapes dans un chat LLM externe ; enregistre JSON et Markdown ici.",
            "empty_state": "Aucun jeu actif. Choisis-en un ou crée le tien.",
        },
        "dialog": {
            "title": "✨ Jeu de questions avec LLM externe",
            "intro": (
                "Un seul chat avec ton **LLM externe** (p. ex. ChatGPT, Claude, Gemini) pour **les quatre étapes**. "
                "Tu enregistres chaque résultat ici :\n\n"
                "1) **Jeu** – prompt étape 1, réponses, enregistrer le JSON.\n"
                "2) **Objectifs** – prompt étape 2 dans le **même chat**, enregistrer le Markdown.\n"
                "3) **Relecture jeu** – prompt étape 3 dans le **même chat**, enregistrer le JSON.\n"
                "4) **Relecture objectifs** – prompt étape 4 dans le **même chat**, enregistrer le Markdown."
            ),
            "intro_info": (
                "MC-Test ne génère pas le contenu. Un chat pour toutes les étapes : copie les prompts vers ton "
                "**LLM externe**, colle ici **uniquement JSON ou Markdown** – sans texte autour."
            ),
            "tab_selector_hint": "Onglets 1–4 = étapes du chat LLM externe. Choisis ce que tu veux enregistrer.",
            "questionset_caption": (
                "Ouvre un nouveau chat avec ton LLM externe, colle le prompt étape 1, réponds, "
                "enregistre le JSON ici. Étapes 2–4 dans le **même chat**."
            ),
            "learning_objectives_caption": (
                "Dans le **même chat avec ton LLM externe** : copie le prompt étape 2. "
                "Enregistre uniquement le Markdown ici."
            ),
            "postproduction_caption": (
                "Dans le **même chat avec ton LLM externe** : copie le prompt étape 3. "
                "Enregistre uniquement le JSON corrigé."
            ),
            "postproduction_lo_caption": (
                "Dans le **même chat avec ton LLM externe** : copie le prompt étape 4. "
                "Enregistre uniquement le Markdown corrigé."
            ),
            "postproduction_set_for_ai_caption": (
                "Seulement si l’historique ne suffit pas : utilise ce JSON dans ton LLM externe."
            ),
            "postproduction_lo_inputs_caption": (
                "Seulement si l’historique ne suffit pas : envoie les deux fichiers avec le prompt au LLM externe."
            ),
            "alternative_caption": "Colle uniquement le bloc JSON du LLM externe – sans texte avant ou après.",
            "learning_objectives_paste_caption": "Colle uniquement le bloc Markdown.",
            "postproduction_paste_caption": "Colle uniquement le bloc JSON corrigé.",
            "postproduction_lo_paste_caption": "Colle uniquement le bloc Markdown corrigé.",
            "ai_bias_title": "Pourquoi les étapes 3 et 4 ?",
            "ai_bias_explanation": (
                "Les LLM produisent souvent des résultats inégaux. Les étapes 3 et 4 lissent jeu et objectifs avant usage."
            ),
        },
    },
    "es": {
        "sidebar": {"create_user_qset": "Conjunto con LLM externo"},
        "welcome": {
            "splash": {
                "create_ai": "Conjunto con LLM externo",
                "hero_subtitle": "Elige un conjunto listo o crea el tuyo en cuatro etapas con un LLM externo.",
            },
            "create_own_set": "🧠 Tu propio conjunto",
            "create_own_set_hint": "Cuatro etapas en un chat con LLM externo; guarda JSON y Markdown aquí.",
            "empty_state": "Ningún conjunto activo. Elige uno o crea el tuyo.",
        },
        "dialog": {
            "title": "✨ Conjunto con LLM externo",
            "intro": (
                "Un solo chat con tu **LLM externo** (p. ej. ChatGPT, Claude, Gemini) para **las cuatro etapas**. "
                "Guarda cada resultado aquí:\n\n"
                "1) **Conjunto** – prompt etapa 1, respuestas, guardar JSON.\n"
                "2) **Objetivos** – prompt etapa 2 en el **mismo chat**, guardar Markdown.\n"
                "3) **Revisión conjunto** – prompt etapa 3 en el **mismo chat**, guardar JSON.\n"
                "4) **Revisión objetivos** – prompt etapa 4 en el **mismo chat**, guardar Markdown."
            ),
            "intro_info": (
                "MC-Test no genera contenido. Un chat para todas las etapas: copia prompts al **LLM externo**, "
                "pega aquí **solo JSON o Markdown** – sin texto extra."
            ),
            "tab_selector_hint": "Pestañas 1–4 = etapas del chat con LLM externo. Elige qué guardar ahora.",
            "questionset_caption": (
                "Abre un chat nuevo con tu LLM externo, pega el prompt etapa 1, responde, guarda el JSON aquí. "
                "Etapas 2–4 en el **mismo chat**."
            ),
            "learning_objectives_caption": (
                "En el **mismo chat con tu LLM externo**: copia el prompt etapa 2. Guarda solo Markdown aquí."
            ),
            "postproduction_caption": (
                "En el **mismo chat con tu LLM externo**: copia el prompt etapa 3. Guarda solo JSON corregido."
            ),
            "postproduction_lo_caption": (
                "En el **mismo chat con tu LLM externo**: copia el prompt etapa 4. Guarda solo Markdown corregido."
            ),
            "postproduction_set_for_ai_caption": (
                "Solo si el historial no basta: usa este JSON en tu LLM externo."
            ),
            "postproduction_lo_inputs_caption": (
                "Solo si el historial no basta: envía ambos archivos con el prompt al LLM externo."
            ),
            "alternative_caption": "Pega solo el bloque JSON del LLM externo – sin texto antes ni después.",
            "learning_objectives_paste_caption": "Pega solo el bloque Markdown.",
            "postproduction_paste_caption": "Pega solo el bloque JSON corregido.",
            "postproduction_lo_paste_caption": "Pega solo el bloque Markdown corregido.",
            "ai_bias_title": "¿Para qué las etapas 3 y 4?",
            "ai_bias_explanation": (
                "Los LLM suelen dar resultados irregulares. Las etapas 3 y 4 alisan conjunto y objetivos antes del uso."
            ),
        },
    },
    "it": {
        "sidebar": {"create_user_qset": "Set con LLM esterno"},
        "welcome": {
            "splash": {
                "create_ai": "Set con LLM esterno",
                "hero_subtitle": "Scegli un set pronto o creane uno in quattro fasi con un LLM esterno.",
            },
            "create_own_set": "🧠 Il tuo set",
            "create_own_set_hint": "Quattro fasi in un chat con LLM esterno; salva JSON e Markdown qui.",
            "empty_state": "Nessun set attivo. Scegline uno o creane uno.",
        },
        "dialog": {
            "title": "✨ Set con LLM esterno",
            "intro": (
                "Un solo chat con il tuo **LLM esterno** (es. ChatGPT, Claude, Gemini) per **tutte e quattro le fasi**. "
                "Salva ogni risultato qui:\n\n"
                "1) **Set** – prompt fase 1, risposte, salva JSON.\n"
                "2) **Obiettivi** – prompt fase 2 nello **stesso chat**, salva Markdown.\n"
                "3) **Revisione set** – prompt fase 3 nello **stesso chat**, salva JSON.\n"
                "4) **Revisione obiettivi** – prompt fase 4 nello **stesso chat**, salva Markdown."
            ),
            "intro_info": (
                "MC-Test non genera contenuti. Un chat per tutte le fasi: copia i prompt nel **LLM esterno**, "
                "incolla qui **solo JSON o Markdown** – senza testo extra."
            ),
            "tab_selector_hint": "Schede 1–4 = fasi del chat con LLM esterno. Scegli cosa salvare ora.",
            "questionset_caption": (
                "Apri un nuovo chat con il tuo LLM esterno, incolla il prompt fase 1, rispondi, salva il JSON qui. "
                "Fasi 2–4 nello **stesso chat**."
            ),
            "learning_objectives_caption": (
                "Nello **stesso chat con il tuo LLM esterno**: copia il prompt fase 2. Salva solo Markdown qui."
            ),
            "postproduction_caption": (
                "Nello **stesso chat con il tuo LLM esterno**: copia il prompt fase 3. Salva solo JSON corretto."
            ),
            "postproduction_lo_caption": (
                "Nello **stesso chat con il tuo LLM esterno**: copia il prompt fase 4. Salva solo Markdown corretto."
            ),
            "postproduction_set_for_ai_caption": (
                "Solo se la cronologia non basta: usa questo JSON nel LLM esterno."
            ),
            "postproduction_lo_inputs_caption": (
                "Solo se la cronologia non basta: invia entrambi i file con il prompt al LLM esterno."
            ),
            "alternative_caption": "Incolla solo il blocco JSON dal LLM esterno – senza testo prima o dopo.",
            "learning_objectives_paste_caption": "Incolla solo il blocco Markdown.",
            "postproduction_paste_caption": "Incolla solo il blocco JSON corretto.",
            "postproduction_lo_paste_caption": "Incolla solo il blocco Markdown corretto.",
            "ai_bias_title": "Perché le fasi 3 e 4?",
            "ai_bias_explanation": (
                "I LLM spesso producono risultati disomogenei. Le fasi 3 e 4 levigano set e obiettivi prima dell’uso."
            ),
        },
    },
    "zh": {
        "sidebar": {"create_user_qset": "使用外部 LLM 创建题库"},
        "welcome": {
            "splash": {
                "create_ai": "使用外部 LLM 创建题库",
                "hero_subtitle": "选择现成题库，或用外部 LLM 分四步创建自己的题库。",
            },
            "create_own_set": "🧠 创建自己的题库",
            "create_own_set_hint": "在外部 LLM 的同一对话中完成四步；在这里保存 JSON 和 Markdown。",
            "empty_state": "当前没有题库。请选择一个或创建自己的题库。",
        },
        "dialog": {
            "title": "✨ 使用外部 LLM 创建题库",
            "intro": (
                "在与**外部 LLM**（如 ChatGPT、Claude、Gemini）的**同一对话**中完成**四个阶段**，并在这里保存每一步结果：\n\n"
                "1) **题库** – 第 1 阶段提示词，回答问题，保存 JSON。\n"
                "2) **学习目标** – 在**同一对话**中使用第 2 阶段提示词，保存 Markdown。\n"
                "3) **检查题库** – 在**同一对话**中使用第 3 阶段提示词，保存 JSON。\n"
                "4) **检查学习目标** – 在**同一对话**中使用第 4 阶段提示词，保存 Markdown。"
            ),
            "intro_info": (
                "MC-Test 不生成内容。四个阶段共用一个对话：把提示词复制到**外部 LLM**，"
                "这里只粘贴**JSON 或 Markdown**——不要附加说明文字。"
            ),
            "tab_selector_hint": "标签 1–4 对应外部 LLM 对话中的四个阶段。选择现在要保存的阶段。",
            "questionset_caption": (
                "用外部 LLM 新建对话，粘贴第 1 阶段提示词，回答问题，在这里保存 JSON。"
                "第 2–4 阶段在**同一对话**中继续。"
            ),
            "alternative_caption": "只粘贴外部 LLM 返回的 JSON 代码块——前后不要加文字。",
            "learning_objectives_caption": (
                "在**与外部 LLM 的同一对话**中继续：复制第 2 阶段提示词。在这里只保存 Markdown。"
            ),
            "postproduction_caption": (
                "在**与外部 LLM 的同一对话**中继续：复制第 3 阶段提示词。在这里只保存整理后的 JSON。"
            ),
            "postproduction_lo_caption": (
                "在**与外部 LLM 的同一对话**中继续：复制第 4 阶段提示词。在这里只保存整理后的 Markdown。"
            ),
            "postproduction_set_for_ai_caption": "仅当对话历史不够时：在外部 LLM 中使用此 JSON。",
            "postproduction_lo_inputs_caption": "仅当对话历史不够时：将两个文件与提示词一起发给外部 LLM。",
            "learning_objectives_paste_caption": "只粘贴 Markdown 代码块。",
            "postproduction_paste_caption": "只粘贴整理后的 JSON 代码块。",
            "postproduction_lo_paste_caption": "只粘贴整理后的 Markdown 代码块。",
            "ai_bias_title": "为什么需要第 3、4 阶段？",
            "ai_bias_explanation": "LLM 输出常不够均衡。第 3、4 阶段在使用前润色题库与学习目标。",
        },
    },
}


SECONDARY_PATCHES: dict[str, dict] = {
    "en": {
        "dialog": {
            "questionset_next_button": "➡️ Next: Stage 2",
            "learning_objectives_next_qa_button": "➡️ Next: Stage 3",
            "postproduction_next_lo_button": "➡️ Next: Stage 4",
        },
    },
    "fr": {
        "dialog": {
            "prompt_guide": "Le **prompt MC-Test** fournit le JSON canonique pour tests, Anki et arsnova.eu.",
            "questionset_heading": "Étape 1 : Jeu de questions",
            "prompt_expander_title": "Prompt étape 1",
            "upload_warning": "⚠️ Max. 30 questions, 5 Mo.",
            "upload_info": "Jeux temporaires : supprimés après {hours} h ; pseudo réservé : {days} jours.",
            "uploader_mode": "Ajouter le JSON",
            "uploader_help": "Max. 30 questions, 5 Mo. Schéma JSON MC-Test.",
            "alternative_heading": "### Ou : coller le JSON",
            "status_error_hint": "Échec d’enregistrement. Voir les détails.",
            "status_json_repair_hint": "Astuce : colle l’erreur dans ton LLM externe – le JSON se répare souvent.",
            "lo_optional_info": "Optionnel : objectifs à l’étape 2 – ou démarrage sans.",
            "login_required": "Connecte-toi pour démarrer.",
            "learning_objectives_heading": "Étape 2 : Objectifs",
            "learning_objectives_hint_save_first": "Termine l’étape 1 et enregistre le JSON.",
            "learning_objectives_mode": "Ajouter les objectifs",
            "learning_objectives_help": "Nom de fichier adapté automatiquement à ton jeu.",
            "learning_objectives_success": "Objectifs enregistrés : {filename}.",
            "questionset_next_step": "Suite : étape 2 – objectifs.",
            "questionset_next_button": "➡️ Étape 2",
            "learning_objectives_prompt_expander": "Prompt étape 2",
            "learning_objectives_original_set_download": "⬇️ JSON (si l’historique manque)",
            "learning_objectives_save_set_first": "Termine l’étape 1 et enregistre le JSON.",
            "learning_objectives_next_qa_button": "➡️ Étape 3",
            "postproduction_heading": "Étape 3 : Relecture du jeu",
            "postproduction_prompt_expander": "Prompt étape 3",
            "postproduction_set_for_ai_download": "⬇️ JSON (si l’historique manque)",
            "postproduction_next_lo_button": "➡️ Étape 4",
            "postproduction_lo_heading": "Étape 4 : Relecture des objectifs",
            "postproduction_lo_prompt_expander": "Prompt étape 4",
            "postproduction_lo_set_download": "⬇️ JSON relu (si besoin)",
            "postproduction_lo_download": "⬇️ Objectifs (si besoin)",
            "postproduction_lo_not_found": "Aucun objectif enregistré pour ce jeu.",
            "postproduction_lo_need_set": "Termine d’abord l’étape 3.",
            "postproduction_lo_need_save": "Enregistre les objectifs avant de démarrer.",
            "postproduction_lo_start_button": "🚀 Démarrer maintenant",
            "questionset_save_success": "Jeu enregistré. Passe à l’étape 2.",
            "learning_objectives_save_success": "Objectifs enregistrés. Étape 3 ou démarrage direct.",
            "learning_objectives_set_loaded": "Actif : « {label} »",
            "postproduction_save_success": "Jeu relu enregistré. Passe à l’étape 4.",
            "postproduction_lo_save_success": "Objectifs enregistrés. Tu peux démarrer.",
            "questionset_start_without_lo_warning": "⚠️ Sans objectifs – rattrapable à l’étape 2.",
            "questionset_start_without_lo_hint": "Objectifs ajoutables à tout moment à l’étape 2.",
        },
        "user_qset": {
            "login_required": "Connecte-toi pour démarrer.",
            "no_questions": "Ce jeu ne contient aucune question.",
            "session_failed": "Démarrage impossible.",
        },
    },
    "es": {
        "dialog": {
            "prompt_guide": "El **prompt MC-Test** genera el JSON canónico para tests, Anki y arsnova.eu.",
            "questionset_heading": "Etapa 1: Conjunto de preguntas",
            "prompt_expander_title": "Prompt etapa 1",
            "upload_warning": "⚠️ Máx. 30 preguntas, 5 MB.",
            "upload_info": "Conjuntos temporales: borrados tras {hours} h; seudónimo reservado: {days} días.",
            "uploader_mode": "Añadir JSON",
            "uploader_help": "Máx. 30 preguntas, 5 MB. Esquema JSON MC-Test.",
            "alternative_heading": "### O: pegar JSON",
            "status_error_hint": "Error al guardar. Ver detalles.",
            "status_json_repair_hint": "Consejo: pega el error en tu LLM externo; suele reparar el JSON.",
            "lo_optional_info": "Opcional: objetivos en etapa 2 – o empezar sin ellos.",
            "login_required": "Inicia sesión para empezar.",
            "learning_objectives_heading": "Etapa 2: Objetivos",
            "learning_objectives_hint_save_first": "Termina la etapa 1 y guarda el JSON.",
            "learning_objectives_mode": "Añadir objetivos",
            "learning_objectives_help": "El nombre del archivo se ajusta automáticamente al conjunto.",
            "learning_objectives_success": "Objetivos guardados: {filename}.",
            "questionset_next_step": "Siguiente: etapa 2 – objetivos.",
            "questionset_next_button": "➡️ Etapa 2",
            "learning_objectives_prompt_expander": "Prompt etapa 2",
            "learning_objectives_original_set_download": "⬇️ JSON (si falta historial)",
            "learning_objectives_save_set_first": "Termina la etapa 1 y guarda el JSON.",
            "learning_objectives_next_qa_button": "➡️ Etapa 3",
            "postproduction_heading": "Etapa 3: Revisar conjunto",
            "postproduction_prompt_expander": "Prompt etapa 3",
            "postproduction_set_for_ai_download": "⬇️ JSON (si falta historial)",
            "postproduction_next_lo_button": "➡️ Etapa 4",
            "postproduction_lo_heading": "Etapa 4: Revisar objetivos",
            "postproduction_lo_prompt_expander": "Prompt etapa 4",
            "postproduction_lo_set_download": "⬇️ JSON revisado (si hace falta)",
            "postproduction_lo_download": "⬇️ Objetivos (si hace falta)",
            "postproduction_lo_not_found": "Aún no hay objetivos guardados para este conjunto.",
            "postproduction_lo_need_set": "Termina primero la etapa 3.",
            "postproduction_lo_need_save": "Guarda los objetivos antes de empezar.",
            "postproduction_lo_start_button": "🚀 Empezar ahora",
            "questionset_save_success": "Conjunto guardado. Continúa con la etapa 2.",
            "learning_objectives_save_success": "Objetivos guardados. Etapa 3 o inicio directo.",
            "learning_objectives_set_loaded": "Activo: «{label}»",
            "postproduction_save_success": "Conjunto revisado guardado. Continúa con la etapa 4.",
            "postproduction_lo_save_success": "Objetivos guardados. Ya puedes empezar.",
            "questionset_start_without_lo_warning": "⚠️ Sin objetivos – puedes añadirlos en la etapa 2.",
            "questionset_start_without_lo_hint": "Puedes añadir objetivos en cualquier momento en la etapa 2.",
        },
        "user_qset": {
            "login_required": "Inicia sesión para empezar.",
            "no_questions": "Este conjunto no contiene preguntas.",
            "session_failed": "No se pudo iniciar.",
        },
    },
    "it": {
        "dialog": {
            "prompt_guide": "Il **prompt MC-Test** produce JSON canonico per test, Anki e arsnova.eu.",
            "questionset_heading": "Fase 1: Set di domande",
            "prompt_expander_title": "Prompt fase 1",
            "upload_warning": "⚠️ Max 30 domande, 5 MB.",
            "upload_info": "Set temporanei: eliminati dopo {hours} h; pseudonimo riservato: {days} giorni.",
            "uploader_mode": "Aggiungi JSON",
            "uploader_help": "Max 30 domande, 5 MB. Schema JSON MC-Test.",
            "alternative_heading": "### Oppure: incolla JSON",
            "status_error_hint": "Salvataggio fallito. Mostra dettagli.",
            "status_json_repair_hint": "Suggerimento: incolla l’errore nel LLM esterno – spesso ripara il JSON.",
            "lo_optional_info": "Opzionale: obiettivi in fase 2 – oppure avvia senza.",
            "login_required": "Accedi per iniziare.",
            "learning_objectives_heading": "Fase 2: Obiettivi",
            "learning_objectives_hint_save_first": "Completa la fase 1 e salva il JSON.",
            "learning_objectives_mode": "Aggiungi obiettivi",
            "learning_objectives_help": "Il nome file viene adattato automaticamente al set.",
            "learning_objectives_success": "Obiettivi salvati: {filename}.",
            "questionset_next_step": "Avanti: fase 2 – obiettivi.",
            "questionset_next_button": "➡️ Fase 2",
            "learning_objectives_prompt_expander": "Prompt fase 2",
            "learning_objectives_original_set_download": "⬇️ JSON (se manca la cronologia)",
            "learning_objectives_save_set_first": "Completa la fase 1 e salva il JSON.",
            "learning_objectives_next_qa_button": "➡️ Fase 3",
            "postproduction_heading": "Fase 3: Revisione set",
            "postproduction_prompt_expander": "Prompt fase 3",
            "postproduction_set_for_ai_download": "⬇️ JSON (se manca la cronologia)",
            "postproduction_next_lo_button": "➡️ Fase 4",
            "postproduction_lo_heading": "Fase 4: Revisione obiettivi",
            "postproduction_lo_prompt_expander": "Prompt fase 4",
            "postproduction_lo_set_download": "⬇️ JSON revisionato (se serve)",
            "postproduction_lo_download": "⬇️ Obiettivi (se serve)",
            "postproduction_lo_not_found": "Nessun obiettivo salvato per questo set.",
            "postproduction_lo_need_set": "Completa prima la fase 3.",
            "postproduction_lo_need_save": "Salva gli obiettivi prima di iniziare.",
            "postproduction_lo_start_button": "🚀 Inizia ora",
            "questionset_save_success": "Set salvato. Continua con la fase 2.",
            "learning_objectives_save_success": "Obiettivi salvati. Fase 3 o avvio diretto.",
            "learning_objectives_set_loaded": "Attivo: «{label}»",
            "postproduction_save_success": "Set revisionato salvato. Continua con la fase 4.",
            "postproduction_lo_save_success": "Obiettivi salvati. Puoi iniziare.",
            "questionset_start_without_lo_warning": "⚠️ Senza obiettivi – recuperabili in fase 2.",
            "questionset_start_without_lo_hint": "Puoi aggiungere obiettivi in qualsiasi momento in fase 2.",
        },
        "user_qset": {
            "login_required": "Accedi per iniziare.",
            "no_questions": "Questo set non contiene domande.",
            "session_failed": "Avvio non riuscito.",
        },
    },
    "zh": {
        "dialog": {
            "prompt_guide": "**MC-Test 提示词** 生成用于测试、Anki 和 arsnova.eu 的规范 JSON。",
            "questionset_heading": "阶段 1：生成题库",
            "prompt_expander_title": "第 1 阶段提示词",
            "upload_warning": "⚠️ 最多 30 题，最大 5 MB。",
            "upload_info": "临时题库：{hours} 小时后删除；保留化名：{days} 天。",
            "uploader_mode": "添加 JSON",
            "uploader_help": "最多 30 题，5 MB。须符合 MC-Test JSON 结构。",
            "alternative_heading": "### 或：粘贴 JSON",
            "alternative_caption": "只粘贴外部 LLM 返回的 JSON 代码块——前后不要加文字。",
            "status_error_hint": "保存失败。查看详情。",
            "status_json_repair_hint": "提示：把错误信息发给外部 LLM——通常可修复 JSON。",
            "lo_optional_info": "可选：在第 2 阶段保存学习目标——或不带学习目标开始。",
            "login_required": "请先登录再开始。",
            "learning_objectives_heading": "阶段 2：生成学习目标",
            "learning_objectives_hint_save_first": "先完成第 1 阶段并保存 JSON。",
            "learning_objectives_mode": "添加学习目标",
            "learning_objectives_help": "文件名会自动匹配题库。",
            "learning_objectives_success": "学习目标已保存：{filename}。",
            "questionset_next_step": "下一步：第 2 阶段——学习目标。",
            "questionset_next_button": "➡️ 第 2 阶段",
            "learning_objectives_prompt_expander": "第 2 阶段提示词",
            "learning_objectives_original_set_download": "⬇️ JSON（对话历史不足时）",
            "learning_objectives_save_set_first": "先完成第 1 阶段并保存 JSON。",
            "learning_objectives_next_qa_button": "➡️ 第 3 阶段",
            "postproduction_heading": "阶段 3：检查题库",
            "postproduction_prompt_expander": "第 3 阶段提示词",
            "postproduction_set_for_ai_download": "⬇️ JSON（对话历史不足时）",
            "postproduction_next_lo_button": "➡️ 第 4 阶段",
            "postproduction_lo_heading": "阶段 4：检查学习目标",
            "postproduction_lo_prompt_expander": "第 4 阶段提示词",
            "postproduction_lo_set_download": "⬇️ 已检查 JSON（如需要）",
            "postproduction_lo_download": "⬇️ 学习目标（如需要）",
            "postproduction_lo_not_found": "此题库尚未保存学习目标。",
            "postproduction_lo_need_set": "请先完成第 3 阶段。",
            "postproduction_lo_need_save": "开始前请先保存学习目标。",
            "postproduction_lo_start_button": "🚀 立即开始",
            "questionset_save_success": "题库已保存。继续第 2 阶段。",
            "learning_objectives_save_success": "学习目标已保存。可进入第 3 阶段或直接开始。",
            "learning_objectives_set_loaded": "当前：「{label}」",
            "postproduction_save_success": "已检查题库已保存。继续第 4 阶段。",
            "postproduction_lo_save_success": "学习目标已保存。可以开始。",
            "tab_selector_label": "阶段（1–4）",
            "questionset_start_without_lo_warning": "⚠️ 无学习目标开始——可在第 2 阶段补做。",
            "questionset_start_without_lo_hint": "可随时在第 2 阶段补充学习目标。",
        },
        "user_qset": {
            "login_required": "请先登录再开始。",
            "no_questions": "此题库不含题目。",
            "session_failed": "无法开始。",
        },
    },
}


def _deep_merge(base: dict, patch: dict) -> dict:
    for key, value in patch.items():
        if isinstance(value, dict) and isinstance(base.get(key), dict):
            _deep_merge(base[key], value)
        else:
            base[key] = value
    return base


def main() -> None:
    merged = {**PATCHES}
    for lang, patch in SECONDARY_PATCHES.items():
        if lang in merged:
            _deep_merge(merged[lang], patch)
        else:
            merged[lang] = patch
    for lang, patch in merged.items():
        path = I18N / f"{lang}.json"
        data = json.loads(path.read_text(encoding="utf-8"))
        _deep_merge(data, patch)
        path.write_text(json.dumps(data, ensure_ascii=False, indent=4) + "\n", encoding="utf-8")
        print(f"updated {path.name}")


if __name__ == "__main__":
    main()
