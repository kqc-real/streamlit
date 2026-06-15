from i18n import translate


def test_flat_dotted_keys_inside_nested_sections_are_resolved_by_locale():
    assert (
        translate("summary_view.export_testbericht_expander.exam", locale="en")
        == "📄 Timed Mode Report (PDF)"
    )
    assert (
        translate("summary_view.export_testbericht_expander.exam", locale="de")
        == "📄 Zeitmodus-Bericht (PDF)"
    )
    assert (
        translate("summary_view.export_testbericht_download.practice", locale="en")
        == "💾 Download Learning Report"
    )


def test_export_report_description_is_locale_specific():
    assert (
        translate("summary_view.export_testbericht_description", locale="de")
        == "Dein PDF-Ergebnisbericht mit Punkten, Antworten und Zeitstatistiken."
    )
    assert (
        translate("summary_view.export_testbericht_description", locale="en")
        == "Your PDF results report with score, answers, and time stats."
    )
