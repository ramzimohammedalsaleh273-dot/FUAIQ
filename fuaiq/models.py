from dataclasses import asdict, dataclass
from typing import Any

@dataclass(frozen=True)
class EnhanceOptions:
    scale: int = 2
    denoise: bool = True
    sharpen: float = 0.35
    contrast: float = 1.03
    max_pixels: int = 40_000_000

    def validate(self) -> None:
        if self.scale not in (1, 2, 4):
            raise ValueError("scale must be one of: 1, 2, 4")
        if not 0.0 <= self.sharpen <= 2.0:
            raise ValueError("sharpen must be between 0 and 2")
        if not 0.5 <= self.contrast <= 1.8:
            raise ValueError("contrast must be between 0.5 and 1.8")
        if self.max_pixels < 1:
            raise ValueError("max_pixels must be positive")

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

@dataclass(frozen=True)
class EnhanceResult:
    input_path: str
    output_path: str
    input_width: int
    input_height: int
    output_width: int
    output_height: int
    elapsed_seconds: float
    pipeline: tuple[str, ...]
    warnings: tuple[str, ...]
    metadata_path: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "input_path": self.input_path, "output_path": self.output_path,
            "input_width": self.input_width, "input_height": self.input_height,
            "output_width": self.output_width, "output_height": self.output_height,
            "elapsed_seconds": round(self.elapsed_seconds, 4), "pipeline": list(self.pipeline),
            "warnings": list(self.warnings), "metadata_path": self.metadata_path,
        }
