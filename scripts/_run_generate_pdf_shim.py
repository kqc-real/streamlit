"""Run PDF generation without requiring the real `streamlit` package.

This script inserts a minimal `streamlit` shim into `sys.modules`, then
imports `pdf_export.generate_pdf_report` and writes the resulting PDF to
`artifacts/test_report.pdf`.

Use only for local testing.
"""
import sys
import os
import types
from datetime import datetime, timedelta

# Ensure repo root is importable
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

# Minimal streamlit shim
st = types.ModuleType("streamlit")
st.session_state = {}
st.session_state.update({
    "user_id": "test_user",
    "selected_questions_file": "questions_sample.json",
    # Make a short test duration
    "test_start_time": datetime.now() - timedelta(seconds=75),
    "test_end_time": datetime.now(),
    "test_manually_ended": True,
    "selected_tempo": "power",
})

sys.modules["streamlit"] = st

def main():
    # Import here so our shim is active
    from pdf_export import generate_pdf_report

    # Simple single-question sample (minimal fields used by the report)
    sample_questions = [
        {
            "frage": "Was ist 2+2?",
            "optionen": ["3", "4", "5"],
            "loesung": 1,
            "gewichtung": 1,
        }
    ]

    # Minimal app_config with test_duration_minutes
    class AppConfig:
        test_duration_minutes = 10
        scoring_mode = "default"

    app_config = AppConfig()

    pdf_bytes = generate_pdf_report(sample_questions, app_config)

    out_dir = os.path.join(ROOT, "artifacts")
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, "test_report.pdf")
    with open(out_path, "wb") as f:
        f.write(pdf_bytes)

    print(f"Wrote PDF to: {out_path}")

if __name__ == "__main__":
    main()
