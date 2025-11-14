import json
import sys
sys.path.insert(0, '.')

from exporters.anki_tsv import transform_to_anki_tsv


def test_ankicts_preserves_math_and_escapes_angle_brackets():
    s_list = [
        "$\\u_1=\\dfrac{v_1}{\\|v_1\\|}$, dann $w_j=v_j-\\sum_{i<j}\\langle v_j,u_i\\rangle u_i$, $u_j=\\dfrac{w_j}{\\|w_j\\|}$.",
        "$w_j=v_j+\\sum_{i<j}\\langle v_j,u_i\\rangle u_i$, $u_j=\\dfrac{v_j}{\\|v_j\\|}$.",
        "$u_j=v_j$, $w_j=\\dfrac{v_j}{\\|v_j\\|}$.",
        "$u_j=\\sum_i v_i$, $w_j=u_j$.",
    ]

    j = {"meta": {"title": "t"}, "questions": [{"frage": "q", "optionen": s_list, "loesung": 0, "erklaerung": "ex"}]}
    tsv = transform_to_anki_tsv(json.dumps(j).encode("utf-8"))

    # math delimiters should survive
    assert "\\(" in tsv and "\\)" in tsv

    # angle brackets inside math must be escaped to avoid being treated
    # as HTML tags by genanki / Anki import
    assert "&lt;" in tsv or "&gt;" in tsv

    # there should be no stray <em> tags inside math fragments
    assert "<em>" not in tsv
