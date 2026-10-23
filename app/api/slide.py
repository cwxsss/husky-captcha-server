import time
from typing import Optional, Dict, Any
from fastapi import APIRouter, Request

from app.core.slide_matcher import solve_slide

router = APIRouter()

@router.post("/api/slide/solve")
@router.post("/slideCaptcha")
@router.post("/api/test/slide-captcha/solve")
async def handle_slide_solve(request: Request):
    data = getattr(request.state, "json_payload", None)
    if data is None:
        try:
            data = await request.json()
        except Exception:
            data = {}
            
    bg_image = data.get("backgroundImage") or data.get("background_image") or ""
    target_image = data.get("targetImage") or data.get("target_image") or ""
    bg_display_w = float(data.get("backgroundDisplayWidth") or data.get("background_display_width") or 0)
    target_display_w = float(data.get("targetDisplayWidth") or data.get("target_display_width") or 0)
    
    meta = data.get("meta") or {}
    request_id = meta.get("requestId") or f"slide_{int(time.time()*1000)}"
    
    if not bg_image:
        return {
            "ok": False,
            "error": {
                "code": "EMPTY_BACKGROUND_IMAGE",
                "message": "滑块背景图数据为空"
            }
        }
        
    result = solve_slide(
        bg_b64=bg_image,
        target_b64=target_image,
        bg_display_width=bg_display_w,
        target_display_width=target_display_w
    )
    
    if "error" in result:
        return {
            "ok": False,
            "error": {
                "code": result["error"],
                "message": "滑块缺口计算失败"
            }
        }
        
    return {
        "ok": True,
        "data": {
            "target": result["target"],
            "distance": result["distance"],
            "request_id": request_id,
            "requestLogId": request_id,
            "method": result.get("method", "ddddocr"),
            "raw_x": result.get("raw_x", 0)
        }
    }

@router.post("/api/slide/sensitive-limit/check")
async def handle_slide_sensitive_check():
    return {"ok": True, "data": {"allowed": True, "remaining": 999999}}

@router.post("/api/slide/sensitive-limit/success")
async def handle_slide_sensitive_success():
    return {"ok": True, "data": {"saved": True}}
