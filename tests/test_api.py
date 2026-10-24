import io
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from fastapi.testclient import TestClient
from PIL import Image

import fuaiq.api as api


class ApiTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.output_dir = Path(self.temp.name)
        self.client = TestClient(api.app)
        self.output_patch = patch.object(api, "OUTPUT_DIR", self.output_dir)
        self.output_patch.start()

    def tearDown(self):
        self.output_patch.stop()
        self.temp.cleanup()

    def _png(self):
        stream = io.BytesIO()
        Image.new("RGB", (16, 12), (80, 120, 160)).save(stream, format="PNG")
        return stream.getvalue()

    def test_health(self):
        response = self.client.get("/health")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["status"], "ok")

    def test_enhance_and_download_result(self):
        response = self.client.post(
            "/v1/enhance",
            files={"file": ("sample.png", self._png(), "image/png")},
            data={"scale": "2", "denoise": "false", "sharpen": "0.2", "contrast": "1.03"},
        )
        self.assertEqual(response.status_code, 200, response.text)
        payload = response.json()
        self.assertEqual(payload["result"]["output_width"], 32)
        self.assertEqual(payload["result"]["output_height"], 24)
        downloaded = self.client.get(payload["download_url"])
        self.assertEqual(downloaded.status_code, 200)
        self.assertEqual(downloaded.headers["content-type"], "image/png")

    def test_rejects_unsupported_extension(self):
        response = self.client.post(
            "/v1/enhance", files={"file": ("notes.txt", b"not an image", "text/plain")}
        )
        self.assertEqual(response.status_code, 415)

    def test_rejects_invalid_result_id(self):
        response = self.client.get("/v1/results/not-a-valid-id")
        self.assertEqual(response.status_code, 400)


if __name__ == "__main__":
    unittest.main()
