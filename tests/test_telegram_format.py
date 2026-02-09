import unittest

from telegram_format import sanitize_telegram_html


class TelegramFormatTests(unittest.TestCase):
    def test_preserves_allowed_tags(self):
        message = "<b>Titulo</b>\n<i>Detalle</i>\n<u>Alerta</u>"
        self.assertEqual(sanitize_telegram_html(message), message)

    def test_converts_markdown_to_html(self):
        message = "**Titulo** y *detalle*"
        sanitised = sanitize_telegram_html(message)
        self.assertIn("<b>Titulo</b>", sanitised)
        self.assertIn("<i>detalle</i>", sanitised)

    def test_escapes_ampersand_and_comparators(self):
        message = "<b>S&P 500</b> < 7000 y > 10"
        sanitised = sanitize_telegram_html(message)
        self.assertIn("<b>S&amp;P 500</b>", sanitised)
        self.assertIn("&lt; 7000", sanitised)
        self.assertIn("&gt; 10", sanitised)

    def test_balances_unclosed_tags(self):
        message = "<b>Alerta <i>critica</b>"
        sanitised = sanitize_telegram_html(message)
        self.assertEqual(sanitised, "<b>Alerta <i>critica</i></b>")

    def test_removes_unsupported_tags(self):
        message = "<div>hola</div><b>ok</b><script>x</script>"
        sanitised = sanitize_telegram_html(message)
        self.assertNotIn("<div>", sanitised)
        self.assertNotIn("<script>", sanitised)
        self.assertIn("hola", sanitised)
        self.assertIn("<b>ok</b>", sanitised)
        self.assertIn("x", sanitised)


if __name__ == "__main__":
    unittest.main()
