import os
import re
import sys

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from telegram_format import sanitize_telegram_html


SAMPLES = {
    "bold": "Titulo: **ALERTA**",
    "italic": "Estado: *inestable*",
    "both": "***riesgo elevado***",
    "heading_bullets": "# Encabezado\n- Item uno\n- Item dos",
    "code": "Codigo: `inline` y ```bloque```",
    "mixed": "Normal __negrita__ y _cursiva_ con **doble**",
    "html_ok": "<b>Ya en HTML</b> y <i>cursiva</i>",
}


def assert_no_markdown(text):
    if "```" in text or "`" in text:
        raise AssertionError("Found backticks in output")
    if re.search(r"[*_]", text):
        raise AssertionError("Found Markdown emphasis markers in output")
    if re.search(r"(?m)^\s*#{1,6}\s+", text):
        raise AssertionError("Found Markdown heading prefix in output")
    if re.search(r"(?m)^\s*[-*•]+\s+", text):
        raise AssertionError("Found Markdown bullet prefix in output")


def assert_expected_transforms(output):
    if "<b>ALERTA</b>" not in output:
        raise AssertionError("Bold markdown did not convert to <b>")
    if "<i>inestable</i>" not in output:
        raise AssertionError("Italic markdown did not convert to <i>")
    if "<b><i>riesgo elevado</i></b>" not in output:
        raise AssertionError("Bold+italic markdown did not convert to <b><i>")
    if "Encabezado" not in output:
        raise AssertionError("Heading content removed unexpectedly")
    if "Item uno" not in output or "Item dos" not in output:
        raise AssertionError("Bullet content removed unexpectedly")
    if "inline" not in output or "bloque" not in output:
        raise AssertionError("Code content removed unexpectedly")
    if "<b>Ya en HTML</b>" not in output or "<i>cursiva</i>" not in output:
        raise AssertionError("Existing HTML tags were stripped")


def main():
    combined = "\n".join(SAMPLES.values())
    sanitised = sanitize_telegram_html(combined)

    assert_no_markdown(sanitised)
    assert_expected_transforms(sanitised)

    print("OK: Telegram HTML sanitiser removed Markdown markers.")


if __name__ == "__main__":
    main()
