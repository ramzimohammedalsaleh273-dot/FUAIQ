import json
import tempfile
import unittest
from pathlib import Path
from PIL import Image
from fuaiq.engine import ImageProcessingError, enhance_image
from fuaiq.models import EnhanceOptions

class EngineTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.source = self.root / "source.png"
        Image.new("RGB", (32, 24), (100, 130, 160)).save(self.source)
    def tearDown(self):
        self.temp.cleanup()
    def test_upscale_and_metadata(self):
        output = self.root / "result.png"
        result = enhance_image(self.source, output, EnhanceOptions(scale=2, denoise=False))
        self.assertEqual((result.output_width, result.output_height), (64, 48))
        self.assertTrue(output.is_file())
        metadata = json.loads(Path(result.metadata_path).read_text(encoding="utf-8"))
        self.assertTrue(metadata["output_verified"])
        self.assertFalse(metadata["claims"]["ai_model_used"])
    def test_original_is_preserved(self):
        before = self.source.read_bytes()
        enhance_image(self.source, self.root / "new.png", EnhanceOptions(scale=1, denoise=False))
        self.assertEqual(self.source.read_bytes(), before)
    def test_refuses_to_overwrite_original(self):
        with self.assertRaises(ImageProcessingError):
            enhance_image(self.source, self.source, EnhanceOptions())
    def test_invalid_scale_is_rejected(self):
        with self.assertRaises(ValueError):
            EnhanceOptions(scale=3).validate()
    def test_output_pixel_limit(self):
        with self.assertRaises(ImageProcessingError):
            enhance_image(self.source, self.root / "too_large.png", EnhanceOptions(scale=4, denoise=False, max_pixels=100))
    def test_missing_input(self):
        with self.assertRaises(ImageProcessingError):
            enhance_image(self.root / "missing.jpg", self.root / "out.png")
    def test_unsupported_output_extension(self):
        with self.assertRaises(ImageProcessingError):
            enhance_image(self.source, self.root / "out.gif", EnhanceOptions())
if __name__ == "__main__":
    unittest.main()
