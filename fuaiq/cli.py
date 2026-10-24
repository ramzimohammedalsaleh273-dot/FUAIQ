import argparse
import json
import sys
from .engine import ImageProcessingError, enhance_image
from .models import EnhanceOptions

def main() -> int:
    parser = argparse.ArgumentParser(prog="fuaiq", description="محرك تحسين الصور فائق")
    sub = parser.add_subparsers(dest="command", required=True)
    command = sub.add_parser("enhance", help="حسّن صورة واحفظ الناتج في ملف منفصل")
    command.add_argument("input", help="مسار الصورة الأصلية")
    command.add_argument("--output", required=True, help="مسار ملف الصورة الناتجة")
    command.add_argument("--scale", type=int, choices=(1, 2, 4), default=2)
    command.add_argument("--no-denoise", action="store_true")
    command.add_argument("--sharpen", type=float, default=0.35)
    command.add_argument("--contrast", type=float, default=1.03)
    command.add_argument("--max-pixels", type=int, default=40_000_000)
    args = parser.parse_args()
    try:
        result = enhance_image(args.input, args.output, EnhanceOptions(
            scale=args.scale, denoise=not args.no_denoise, sharpen=args.sharpen,
            contrast=args.contrast, max_pixels=args.max_pixels))
        print(json.dumps(result.to_dict(), ensure_ascii=False, indent=2))
        return 0
    except (ImageProcessingError, ValueError) as exc:
        print(f"خطأ: {exc}", file=sys.stderr)
        return 2

if __name__ == "__main__":
    raise SystemExit(main())
