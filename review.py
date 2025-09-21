"""Review- und Analyse-Funktionen (Admin-Panel) ausgelagert aus mc_test_app.py.

Enthält:
- display_admin_full_review
- display_admin_panel

Abhängigkeiten zu globalen Konstanten (LOGFILE, FRAGEN_ANZAHL) werden lazily
über das Hauptmodul mc_test_app nachgeladen, um zirkulare Importe zu vermeiden.
"""
from __future__ import annotations
import os
import pandas as pd
import streamlit as st

# Lazy access helpers -------------------------------------------------------

def _get_main_attr(name: str, default=None):  # pragma: no cover - defensive
    try:
        from . import mc_test_app as _app  # type: ignore
        return getattr(_app, name, default)
    except Exception:
        return default


LOGFILE = _get_main_attr("LOGFILE", os.path.join(os.path.dirname(__file__), "mc_test_answers.csv"))
FRAGEN_ANZAHL = _get_main_attr("FRAGEN_ANZAHL", 0)


def display_admin_full_review():
    # Hinweis entfernt: ehem. Sidebar-Meldung 'Admin‑Analyse aktiv – Auswertung im Hauptbereich sichtbar.'
    st.markdown("## 🧪 Gesamtübersicht aller Fragen")
    st.caption(
        "Metadaten: Schwierigkeitsgrad = Lösungsquote; Trennschärfe = Punkt-Biserial (Item vs. Gesamt ohne Item)."
    )
    if not (os.path.isfile(LOGFILE) and os.path.getsize(LOGFILE) > 0):
        st.info("Noch keine Antworten erfasst – es liegen keine Daten für die Auswertung vor.")
        return
    try:
        df = pd.read_csv(LOGFILE, on_bad_lines="skip")
    except Exception as e:  # pragma: no cover
        st.error(f"Antwort-Log konnte nicht geladen werden: {e}")
        return
    if df.empty:
        st.info("Log-Datei ist leer – noch keine Einträge vorhanden.")
        return
    required_cols = {"frage_nr", "frage", "antwort", "richtig", "user_id_hash"}
    if not required_cols.issubset(set(df.columns)):
        st.warning("Log-Datei unvollständig – Auswertung möglicherweise eingeschränkt.")
    df["is_correct"] = df["richtig"].apply(
        lambda x: 1
        if pd.to_numeric(x, errors="coerce") and int(pd.to_numeric(x, errors="coerce") or 0) > 0
        else 0
    )
    grouped = df.groupby(["frage_nr", "frage"], as_index=False).agg(
        n_answers=("antwort", "count"),
        n_correct=("is_correct", "sum"),
    )
    grouped["correct_pct"] = grouped.apply(
        lambda r: (r.n_correct / r.n_answers * 100) if r.n_answers else 0, axis=1
    )
    user_totals = (
        df.groupby("user_id_hash", as_index=False)["is_correct"].sum().rename(
            columns={"is_correct": "total_correct_all"}
        )
    )
    df = df.merge(user_totals, on="user_id_hash", how="left")
    df["total_correct_excl"] = df["total_correct_all"] - df["is_correct"]

    def _point_biserial(sub: pd.DataFrame) -> float:
        if sub["is_correct"].nunique() < 2:
            return float("nan")
        if sub["total_correct_excl"].nunique() < 2:
            return float("nan")
        try:
            return float(sub["is_correct"].corr(sub["total_correct_excl"]))
        except Exception:
            return float("nan")

    discrim = (
        df.groupby("frage_nr")
        .apply(_point_biserial)
        .reset_index(name="discrimination_pb")
    )
    grouped = grouped.merge(discrim, on="frage_nr", how="left")

    def _disc_label(x: float) -> str:
        if pd.isna(x):
            return "—"
        if x >= 0.40:
            return "sehr gut"
        if x >= 0.30:
            return "gut"
        if x >= 0.20:
            return "mittel"
        return "schwach"

    def _difficulty_label(pct: float) -> str:
        if pct < 30:
            return "schwierig"
        if pct <= 70:
            return "mittel"
        return "leicht"

    wrong_df = df[df["is_correct"] == 0]
    if not wrong_df.empty:
        most_wrong = (
            wrong_df.groupby(["frage_nr", "antwort"]).size().reset_index(name="count")
        )
        idx = most_wrong.groupby("frage_nr")["count"].idxmax()
        most_wrong_top = most_wrong.loc[idx][["frage_nr", "antwort", "count"]]
        grouped = grouped.merge(most_wrong_top, on="frage_nr", how="left")
        grouped.rename(
            columns={"antwort": "häufigste_falsche_antwort", "count": "falsch_anzahl"},
            inplace=True,
        )
    else:
        grouped["häufigste_falsche_antwort"] = None
        grouped["falsch_anzahl"] = 0
    grouped["dominanter_distraktor_pct"] = grouped.apply(
        lambda r: (r.falsch_anzahl / r.n_answers * 100) if r.n_answers else 0, axis=1
    )
    grouped["Schwierigkeitsgrad"] = grouped["correct_pct"].map(_difficulty_label)
    grouped["Trennschärfe"] = grouped["discrimination_pb"].map(_disc_label)
    grouped = grouped.sort_values(
        by=["correct_pct", "discrimination_pb", "n_answers"],
        ascending=[True, False, True],
    )
    show_cols = [
        "frage_nr",
        "n_answers",
        "n_correct",
        "correct_pct",
        "Schwierigkeitsgrad",
        "discrimination_pb",
        "Trennschärfe",
        "häufigste_falsche_antwort",
        "falsch_anzahl",
        "dominanter_distraktor_pct",
    ]
    styled = grouped[show_cols].copy()
    styled.rename(
        columns={
            "frage_nr": "Frage-Nr.",
            "n_answers": "Antworten (gesamt)",
            "n_correct": "Richtig",
            "correct_pct": "Richtig % (roh)",
            "discrimination_pb": "Trennschärfe (r_pb)",
            "häufigste_falsche_antwort": "Häufigste falsche Antwort",
            "falsch_anzahl": "Häufigkeit dieser falschen",
            "dominanter_distraktor_pct": "Domin. Distraktor %",
        },
        inplace=True,
    )
    styled["Richtig %"] = grouped["correct_pct"].map(lambda v: f"{v:.1f}%")
    styled["Domin. Distraktor %"] = grouped["dominanter_distraktor_pct"].map(
        lambda v: f"{v:.1f}%" if v else "—"
    )
    styled["Trennschärfe (r_pb)"] = styled["Trennschärfe (r_pb)"].map(
        lambda v: f"{v:.2f}" if pd.notna(v) else "—"
    )
    st.dataframe(styled, use_container_width=True)
    with st.expander("🔎 Detail zu einer ausgewählten Frage"):
        frage_nums = grouped["frage_nr"].tolist()
        sel = (
            st.selectbox(
                "Frage auswählen",
                frage_nums,
                format_func=lambda x: f"Frage {x}",
            )
            if frage_nums
            else None
        )
        if sel is not None:
            detail = df[df["frage_nr"] == sel].copy()
            st.markdown(f"### Frage {sel}: Verlauf & Antworten")
            frage_text_series = grouped[grouped["frage_nr"] == sel]["frage"]
            if not frage_text_series.empty:
                raw_text = frage_text_series.iloc[0]
                try:
                    text_only = raw_text.split(".", 1)[1].strip()
                except Exception:
                    text_only = raw_text
                st.write(f"**Fragentext:** {text_only}")
            st.write("Antwortverlauf (chronologisch, älteste zuerst):")
            detail_sorted = detail[["user_id_hash", "antwort", "richtig", "zeit"]].sort_values(
                by="zeit"
            )
            st.dataframe(detail_sorted, use_container_width=True)
            st.write("Antwortverteilung (Optionen – Häufigkeit & Anteil):")
            dist = (
                detail.groupby(["antwort"], as_index=False)
                .agg(
                    anzahl=("antwort", "count"),
                    korrekt=("is_correct", "max"),
                )
                .sort_values(by="anzahl", ascending=False)
            )
            total = dist["anzahl"].sum() or 1
            dist["Anteil %"] = dist["anzahl"].map(lambda v: f"{v / total * 100:.1f}%")
            dist.rename(
                columns={
                    "antwort": "Option",
                    "anzahl": "Anzahl",
                    "korrekt": "Ist richtig",
                },
                inplace=True,
            )
            dist["Ist richtig"] = dist["Ist richtig"].map(lambda x: "✅" if x else "❌")
            st.dataframe(dist, use_container_width=True)


def display_admin_panel():
    st.sidebar.success("Admin-Modus aktiv")
    tab_analysis, tab_export, tab_system, tab_glossary = st.tabs([
        "📊 Analyse",
        "📤 Export",
        "🛠 System",
        "📚 Glossar",
    ])
    with tab_analysis:
        display_admin_full_review()
    with tab_export:
        st.markdown("### Export / Downloads")
        if os.path.isfile(LOGFILE) and os.path.getsize(LOGFILE) > 0:
            try:
                df_log = pd.read_csv(LOGFILE, on_bad_lines="skip")
                csv_bytes = df_log.to_csv(index=False).encode("utf-8")
                st.download_button(
                    "Antwort-Log (CSV) herunterladen",
                    data=csv_bytes,
                    file_name="mc_test_answers_export.csv",
                    mime="text/csv",
                )
                st.write("Spalten:", ", ".join(df_log.columns))
            except Exception as e:  # pragma: no cover
                st.error(f"Export fehlgeschlagen: {e}")
        else:
            st.info("Kein Log vorhanden.")
    with tab_system:
        st.markdown("### System / Konfiguration")
        st.write("Benutzer (Session):", st.session_state.get("user_id"))
        st.write("Admin-User aktiv:", bool(os.getenv("MC_TEST_ADMIN_USER")))
        st.write(
            "Admin-Key-Modus:",
            "Hash/Klartext gesetzt" if os.getenv("MC_TEST_ADMIN_KEY") else "DEV / keiner gesetzt",
        )
        st.write("Anzahl geladene Fragen:", FRAGEN_ANZAHL)
        st.write(
            "Antworten im Log:", (
                sum(1 for _ in open(LOGFILE, "r", encoding="utf-8")) - 1
                if os.path.isfile(LOGFILE) and os.path.getsize(LOGFILE) > 0
                else 0
            ),
        )
        if os.path.isfile(LOGFILE) and os.path.getsize(LOGFILE) > 0:
            try:
                df_sys = pd.read_csv(LOGFILE, on_bad_lines="skip")
                if not df_sys.empty:
                    unique_users = df_sys["user_id_hash"].nunique()
                    st.write("Eindeutige Teilnehmer (gesamt):", unique_users)
                    if "zeit" in df_sys.columns:
                        try:
                            df_sys["_ts"] = pd.to_datetime(df_sys["zeit"], errors="coerce")
                            last_ts = df_sys["_ts"].max()
                            if pd.notna(last_ts):
                                st.write("Letzte Aktivität:", last_ts)
                                cutoff = last_ts - pd.Timedelta(minutes=10)
                                active_users = df_sys[df_sys["_ts"] >= cutoff]["user_id_hash"].nunique()
                                st.write("Aktive Nutzer (<10 min):", active_users)
                        except Exception:
                            pass
                    ans_per_user = (
                        df_sys.groupby("user_id_hash")["frage_nr"].count().mean()
                        if unique_users > 0
                        else 0
                    )
                    st.write("Ø Antworten je Teilnehmer:", f"{ans_per_user:.1f}")
                    if "richtig" in df_sys.columns:
                        try:
                            df_sys["_corr"] = df_sys["richtig"].apply(
                                lambda x: 1
                                if pd.to_numeric(x, errors="coerce") and int(pd.to_numeric(x, errors="coerce") or 0) > 0
                                else 0
                            )
                            overall_acc = df_sys["_corr"].mean() * 100 if len(df_sys) else 0
                            st.write("Gesamt-Accuracy aller Antworten:", f"{overall_acc:.1f}%")
                        except Exception:
                            pass
            except Exception as e:  # pragma: no cover
                st.warning(f"Erweiterte Metriken nicht verfügbar: {e}")
    with tab_glossary:
        st.markdown("### Glossar Itemanalyse")
        st.write("Kurze Referenz zu allen angezeigten Kennzahlen der Itemanalyse und deren Interpretation.")
        glossary = [
            {"Begriff": "Antworten (gesamt)", "Erklärung": "Alle abgegebenen Antworten zum Item."},
            {"Begriff": "Richtig", "Erklärung": "Anzahl richtiger Antworten (richtig > 0)."},
            {"Begriff": "Richtig % (roh)", "Erklärung": "Prozent richtiger Antworten (p-Wert)."},
            {"Begriff": "Schwierigkeitsgrad", "Erklärung": "p<30% schwierig, 30–70% mittel, >70% leicht."},
            {"Begriff": "Trennschärfe (r_pb)", "Erklärung": "Korrelation Item (0/1) vs. Gesamtscore (ohne Item)."},
            {"Begriff": "Trennschärfe", "Erklärung": "≥0.40 sehr gut, ≥0.30 gut, ≥0.20 mittel, sonst schwach."},
            {"Begriff": "Häufigste falsche Antwort", "Erklärung": "Meistgewählter Distraktor (nur falsche)."},
            {"Begriff": "Häufigkeit dieser falschen", "Erklärung": "Absolute Häufigkeit dieses Distraktors."},
            {"Begriff": "Domin. Distraktor %", "Erklärung": "Anteil meistgewählter Distraktor an allen Antworten."},
            {"Begriff": "Verteilung (Detail)", "Erklärung": "Optionen mit Häufigkeit, Anteil, korrekt?"},
            {"Begriff": "Ø Antworten je Teilnehmer", "Erklärung": "Durchschnitt Antworten pro Nutzer (System)."},
            {"Begriff": "Gesamt-Accuracy", "Erklärung": "Globaler Prozentanteil korrekter Antworten."},
        ]
        st.write("**Interpretationshinweise**:")
        st.markdown("- Günstiger p-Bereich oft 30%–85%.")
        st.markdown("- Trennschärfe <0.20: Item kritisch prüfen.")
        st.markdown("- >90% richtig + niedrige Trennschärfe: evtl. zu leicht.")
        st.markdown("- Dominanter Distraktor >40% + niedriger p: Missverständnis prüfen.")
        st.markdown("- Verteilung zeigt selten genutzte oder überdominante Optionen.")
        st.divider()
        df_gloss = pd.DataFrame(glossary)
        st.dataframe(df_gloss, use_container_width=True, hide_index=True)
        st.divider()
        st.markdown("#### Formeln")
        st.latex(r"p = \frac{Richtig}{Antworten\ gesamt}")
        st.latex(r"r_{pb} = \frac{\bar{X}_1 - \bar{X}_0}{s_X} \sqrt{\frac{n_1 n_0}{n(n-1)}}")
        st.caption(
            "r_{pb}: punkt-biseriale Korrelation; X ohne aktuelles Item; n_1 korrekt, n_0 falsch. "
            "Vereinfachte Form – alternative Schreibweisen möglich."
        )
        st.latex(r"Dominanter\ Distraktor\ % = \frac{Häufigkeit\ stärkster\ Distraktor}{Antworten\ gesamt} \times 100")
        st.caption(
            "Bei sehr kleinem n (<20) Kennzahlen mit Vorsicht interpretieren; Varianz und Korrelationen sind instabil."
        )
        st.divider()
