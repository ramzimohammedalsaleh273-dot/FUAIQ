import json
import time
from pathlib import Path
from typing import Any

import numpy as np
from PIL import Image, ImageEnhance, ImageFilter, ImageOps
from .models import EnhanceOptions, EnhanceResult

try:
    import cv2
except ImportError:
    cv2 = None

SUPPORTED_FORMATS = {".jpg", ".jpeg", ".png", ".webp", ".bmp", ".tif", ".tiff"}

class ImageProcessingError(RuntimeError):
    """Expected, user-correctable image processing failure."""

def _load_image(path: Path, max_pixels: int) -> Image.Image:
    if not path.exists() or not path.is_file():
        raise ImageProcessingError(f"Input image does not exist: {path}")
    if path.suffix.lower() not in SUPPORTED_FORMATS:
        raise ImageProcessingError(f"Unsupported image format: {path.suffix or '(no extension)'}")
    try:
        with Image.open(path) as source:
            source.load()
            if source.width * source.height > max_pixels:
                raise ImageProcessingError(f"Input exceeds pixel limit ({source.width * source.height:,} > {max_pixels:,}).")
            return ImageOps.exif_transpose(source).convert("RGB")
    except ImageProcessingError:
        raise
    except Exception as exc:
        raise ImageProcessingError(f"Could not read image: {exc}") from exc

def _denoise(image: Image.Image) -> Image.Image:
    if cv2 is None:
        return image.filter(ImageFilter.MedianFilter(size=3))
    rgb = np.asarray(image)
    bgr = cv2.cvtColor(rgb, cv2.COLOR_RGB2BGR)
    cleaned = cv2.fastNlMeansDenoisingColored(bgr, None, 3, 3, 7, 21)
    return Image.fromarray(cv2.cvtColor(cleaned, cv2.COLOR_BGR2RGB))

def enhance_image(input_path, output_path, options=None) -> EnhanceResult:
    started = time.perf_counter()
    source_path = Path(input_path).expanduser().resolve()
    destination = Path(output_path).expanduser().resolve()
    opts = options or EnhanceOptions()
    opts.validate()
    if source_path == destination:
        raise ImageProcessingError("Output path must differ from the original image path.")
    if destination.suffix.lower() not in {".png", ".jpg", ".jpeg", ".webp", ".tif", ".tiff"}:
        raise ImageProcessingError("Output extension must be PNG, JPEG, WebP, or TIFF.")

    original = _load_image(source_path, opts.max_pixels)
    result = original.copy()
    pipeline = ["exif_transpose", "convert_rgb"]
    warnings = [
        "Baseline processing only; no specialized motion-deblur or AI super-resolution model.",
        "Upscaling increases pixel dimensions but cannot guarantee recovery of missing source detail.",
    ]
    if opts.denoise:
        result = _denoise(result)
        pipeline.append("conservative_denoise")
    if opts.contrast != 1.0:
        result = ImageEnhance.Contrast(result).enhance(opts.contrast)
        pipeline.append("contrast_adjustment")
    if opts.sharpen > 0:
        result = result.filter(ImageFilter.UnsharpMask(radius=1.2, percent=int(80 * opts.sharpen), threshold=3))
        pipeline.append("unsharp_mask")
    if opts.scale > 1:
        width, height = result.size
        target = (width * opts.scale, height * opts.scale)
        if target[0] * target[1] > opts.max_pixels:
            raise ImageProcessingError(f"Requested output exceeds pixel limit ({target[0] * target[1]:,}). Choose a smaller scale.")
        result = result.resize(target, Image.Resampling.LANCZOS)
        pipeline.append(f"lanczos_upscale_{opts.scale}x")

    destination.parent.mkdir(parents=True, exist_ok=True)
    try:
        save_kwargs: dict[str, Any] = {}
        if destination.suffix.lower() in {".jpg", ".jpeg"}:
            save_kwargs.update(quality=95, optimize=True)
        result.save(destination, **save_kwargs)
        with Image.open(destination) as check:
            check.verify()
    except Exception as exc:
        destination.unlink(missing_ok=True)
        raise ImageProcessingError(f"Could not safely save output image: {exc}") from exc

    elapsed = time.perf_counter() - started
    metadata_path = destination.with_suffix(destination.suffix + ".json")
    metadata = {
        "engine_version": "0.1.0", "input": str(source_path), "output": str(destination),
        "options": opts.to_dict(), "pipeline": pipeline, "warnings": warnings,
        "elapsed_seconds": round(elapsed, 4), "output_verified": True,
        "claims": {"ai_model_used": False, "specialized_motion_deblur_used": False, "super_resolution_model_used": False},
    }
    metadata_path.write_text(json.dumps(metadata, ensure_ascii=False, indent=2), encoding="utf-8")
    return EnhanceResult(str(source_path), str(destination), original.width, original.height,
        result.width, result.height, elapsed, tuple(pipeline), tuple(warnings), str(metadata_path))
