import os
import tempfile
import uuid
from pathlib import Path

from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from fastapi.responses import FileResponse
from starlette.concurrency import run_in_threadpool

from .engine import ImageProcessingError, enhance_image
from .models import EnhanceOptions

app = FastAPI(title="FUAIQ API", version="0.1.0",
              description="Local development API; not hardened for public production.")
MAX_UPLOAD_MB = max(1, min(int(os.getenv("FUAIQ_MAX_UPLOAD_MB", "20")), 100))
OUTPUT_DIR = Path(os.getenv("FUAIQ_OUTPUT_DIR", "./data/outputs")).resolve()
ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp", ".bmp", ".tif", ".tiff"}

@app.get("/health")
def health():
    return {"status": "ok", "service": "fuaiq-api", "version": "0.1.0"}

@app.post("/v1/enhance")
async def enhance(file: UploadFile = File(...), scale: int = Form(2),
                  denoise: bool = Form(True), sharpen: float = Form(0.35),
                  contrast: float = Form(1.03)):
    suffix = Path(file.filename or "").suffix.lower()
    if suffix not in ALLOWED_EXTENSIONS:
        raise HTTPException(status_code=415, detail="صيغة الصورة غير مدعومة.")
    data = await file.read(MAX_UPLOAD_MB * 1024 * 1024 + 1)
    if len(data) > MAX_UPLOAD_MB * 1024 * 1024:
        raise HTTPException(status_code=413, detail=f"الحد الأقصى {MAX_UPLOAD_MB} ميجابايت.")
    job_id = uuid.uuid4().hex
    input_dir = Path(tempfile.gettempdir()) / "fuaiq-inputs"
    input_dir.mkdir(parents=True, exist_ok=True)
    input_path = input_dir / f"{job_id}{suffix}"
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    output_path = OUTPUT_DIR / f"{job_id}.png"
    try:
        input_path.write_bytes(data)
        result = enhance_image(input_path, output_path,
            EnhanceOptions(scale=scale, denoise=denoise, sharpen=sharpen, contrast=contrast))
        return {"job_id": job_id, "result": result.to_dict(),
                "download_url": f"/v1/results/{job_id}",
                "note": "المعالجة الحالية تقليدية وليست ترميمًا متخصصًا بالذكاء الاصطناعي."}
    except (ImageProcessingError, ValueError) as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    finally:
        input_path.unlink(missing_ok=True)

@app.get("/v1/results/{job_id}")
def get_result(job_id: str):
    if len(job_id) != 32 or any(c not in "0123456789abcdef" for c in job_id):
        raise HTTPException(status_code=400, detail="معرّف النتيجة غير صالح.")
    path = OUTPUT_DIR / f"{job_id}.png"
    if not path.is_file():
        raise HTTPException(status_code=404, detail="النتيجة غير موجودة.")
    return FileResponse(path, media_type="image/png", filename=f"fuaiq-{job_id}.png")
