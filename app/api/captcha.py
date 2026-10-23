import hashlib
import time
from typing import Optional, Dict, Any
from fastapi import APIRouter, Request, Response
from pydantic import BaseModel

from app.core.ocr_engine import recognize_captcha
from app.config import settings

router = APIRouter()

class CaptchaRequest(BaseModel):
    image: Optional[str] = ""
    type: Optional[str] = "general"
    meta: Optional[Dict[str, Any]] = None
    quotaCode: Optional[str] = ""

@router.post("/captcha")
async def handle_captcha(request: Request):
    # Retrieve body dict (middleware may have already unpacked protected payload)
    data = getattr(request.state, "json_payload", None)
    if data is None:
        try:
            data = await request.json()
        except Exception:
            data = {}
            
    image_str = data.get("image", "")
    captcha_type = data.get("type", "general")
    meta = data.get("meta") or {}
    request_id = meta.get("requestId") or f"req_{int(time.time()*1000)}"
    
    if not image_str:
        return {
            "ok": False,
            "error": {
                "code": "EMPTY_IMAGE",
                "message": "图片数据为空"
            }
        }
        
    img_hash = hashlib.sha256(image_str.encode("utf-8")).hexdigest()
    recognized_val, debug_info = recognize_captcha(image_str, captcha_type)
    
    return {
        "ok": True,
        "data": {
            "value": recognized_val,
            "captcha_type": captcha_type,
            "request_id": request_id,
            "requestLogId": request_id,
            "image_hash": img_hash,
            "daily_request_limit": settings.DAILY_LIMIT,
            "daily_request_remaining": settings.DAILY_LIMIT,
            "daily_request_used": 1,
            "quota_source": "self_hosted_unlimited",
            "debug": debug_info
        },
        "notice": {
            "key": "captcha_success",
            "enabled": True,
            "level": "ok",
            "message": "获取验证码成功",
            "display_message": "获取验证码成功",
            "should_show": False
        }
    }

@router.post("/captcha-feedback")
async def handle_captcha_feedback(request: Request):
    return {"ok": True, "data": {"saved": True, "message": "Feedback received"}}
