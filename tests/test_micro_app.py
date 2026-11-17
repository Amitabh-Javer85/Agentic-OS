"""End-to-end acceptance checks for the offline Evidence Desk micro-app."""

import tempfile
import unittest
from pathlib import Path

try:
    from playwright.sync_api import sync_playwright
except ImportError as exc:
    raise SystemExit(
        "Browser acceptance tests require optional Playwright: "
        "python -m pip install playwright; python -m playwright install chromium"
    ) from exc


APP = Path(__file__).resolve().parents[1] / "apps" / "research-brief.html"


class EvidenceDeskTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.playwright = sync_playwright().start()
        try:
            cls.browser = cls.playwright.chromium.launch(headless=True)
        except Exception:
            cls.playwright.stop()
            raise

    @classmethod
    def tearDownClass(cls):
        cls.browser.close()
        cls.playwright.stop()

    def setUp(self):
        self.page = self.browser.new_page(accept_downloads=True)
        self.requests = []
        self.errors = []
        self.page.on("request", lambda request: self.requests.append(request.url))
        self.page.on("pageerror", lambda error: self.errors.append(str(error)))
        self.page.goto(APP.as_uri())

    def tearDown(self):
        self.assertEqual(self.errors, [])
        self.assertFalse(any(url.startswith(("http:", "https:")) for url in self.requests))
        self.page.close()

    def test_demo_build_and_download(self):
        self.page.get_by_role("button", name="Load fictional demo").click()
        self.page.get_by_role("button", name="Build brief").click()
        brief = self.page.locator("#preview").inner_text()
        self.assertIn("2 sources included", self.page.locator("#status").inner_text())
        self.assertIn("### [S1] Fictional garden trial / observation log", brief)
        self.assertIn("> Plot A used drip irrigation for four weeks. Water use fell from 100 to 70 litres per week.", brief)
        self.assertIn("### [S2] Fictional garden trial / interview notes", brief)
        self.assertIn("No time measurements were recorded.", brief)
        self.assertIn("No model, network request, or factual verification was used.", brief)
        with self.page.expect_download() as captured:
            self.page.get_by_role("button", name="Download Markdown").click()
        download = captured.value
        self.assertEqual(download.suggested_filename, "fictional-garden-irrigation-trial.md")
        with tempfile.TemporaryDirectory() as temporary:
            target = Path(temporary) / download.suggested_filename
            download.save_as(target)
            self.assertEqual(target.read_text(encoding="utf-8"), self.page.locator("#preview").text_content())
        self.page.locator("#topic").fill("Changed title")
        self.assertTrue(self.page.locator("#download").is_disabled())
        self.assertTrue(self.page.locator("#preview").is_hidden())

    def test_validation_and_literal_html(self):
        self.page.locator("#sources").fill("Missing source body")
        self.page.get_by_role("button", name="Build brief").click()
        self.assertIn("needs a title and notes", self.page.locator("#status").inner_text())
        self.assertTrue(self.page.locator("#download").is_disabled())
        self.page.locator("#sources").fill("\n---\n".join(f"Source {i}\nA note." for i in range(11)))
        self.page.get_by_role("button", name="Build brief").click()
        self.assertIn("no more than 10", self.page.locator("#status").inner_text())
        payload = '<img src=x onerror="window.injected=true">'
        self.page.locator("#sources").fill(f"Untrusted source\n{payload}\nA factual sentence.")
        self.page.get_by_role("button", name="Build brief").click()
        self.assertIn(payload, self.page.locator("#preview").inner_text())
        self.assertEqual(self.page.locator("#preview img").count(), 0)
        self.assertIsNone(self.page.evaluate("window.injected"))


if __name__ == "__main__":
    unittest.main(verbosity=2)
