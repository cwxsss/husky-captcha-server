import time
from fastapi import APIRouter, Request

router = APIRouter()

@router.get("/api/userscript/config")
@router.post("/api/userscript/config")
async def get_userscript_config(request: Request):
    """
    Returns global configuration for the userscript.
    Crucially: sets updateGate.required = False so self-hosted users are never blocked.
    """
    return {
        "ok": True,
        "data": {
            "version": 1,
            "configVersion": "2026-10-23 00:00",
            "config_version": "2026-10-23 00:00",
            "features": {
                "slide_enabled": True,
                "event_upload_enabled": True,
                "slide_china_rollout_percent": 100
            },
            "updateGate": {
                "enabled": False,
                "required": False,
                "minVersion": "1.00",
                "message": ""
            },
            "update_gate": {
                "enabled": False,
                "required": False,
                "min_version": "1.00",
                "message": ""
            },
            "errorNotices": {},
            "interactionNotices": {},
            "rules": {
                "keyword_re": "(captcha|re[\\s-]?captcha|h[\\s-]?captcha|verify|verification|validate|validation|challenge|security|human|robot|anti[-\\s]?bot|not\\s+a\\s+robot|prove\\s+you\\s+are\\s+human|confirm\\s+you\\s+are\\s+human|slider|puzzle|验证码|校验|验证|安全验证|人机|真人|机器人|不是机器人|滑块|拼图|图形验证|行为验证)",
                "negative_keyword_re": "(qrcode|qr[-_ ]?code|二维码)",
                "slide_success_re": "(success|successful|succeeded|passed|validated|verified|complete|completed|done|solved|approved|accepted|verified\\s+successfully|通过|成功|完成|已完成|已通过)",
                "slide_fail_re": "((验证|校验|滑动|拖动)?(失败|错误|未通过)|(请)?重新?(尝试|验证|校验|重试)|再试一次|fail(ed|ure)?|error|retry|again|invalid|incorrect|expired|timeout|timed\\s*out|mismatch|not\\s+match|too\\s+many|rate[-\\s]?limited|try\\s*again|please\\s*(retry|try\\s*again|drag\\s*again)|verification\\s*failed|validation\\s*failed|无效|过期|超时|不匹配|次数过多|操作过快)"
            },
            "shared_slide_binding": {
                "candidate_count": 0,
                "conflict": False,
                "items": [],
                "status": "empty"
            },
            "slide": {
                "collect_enabled": True,
                "dispatch_enabled": True,
                "max_attempts_per_popup": 5,
                "templates": []
            },
            "announcements": []
        }
    }

@router.get("/api/userscript/page-config")
@router.post("/api/userscript/page-config")
async def get_userscript_page_config(request: Request, host: str = "", pathname: str = "/"):
    """
    Returns page-level configuration and bindings.
    """
    now_ms = int(time.time() * 1000)
    return {
        "ok": True,
        "data": {
            "host": host or "default",
            "pathname": pathname or "/",
            "cache_ttl_seconds": 3600,
            "fetch_min_interval_seconds": 30,
            "normal_shared_binding": {
                "candidate_count": 0,
                "confidence": "low",
                "items": [],
                "status": "empty"
            },
            "shared_slide_binding": {
                "candidate_count": 0,
                "conflict": False,
                "items": [],
                "status": "empty"
            },
            "slide_trajectory": {
                "collect_enabled": True,
                "dispatch_enabled": False,
                "max_attempts_per_popup": 5,
                "templates": []
            },
            "client_proof": {
                "enabled": True,
                "version": 1,
                "nonce": "self_hosted_nonce",
                "issued_at_ms": now_ms,
                "expires_at_ms": now_ms + 86400000,
                "signature": "self_hosted_signature"
            },
            "trace_upload": {
                "normal_enabled": False,
                "slide_enabled": False
            }
        }
    }

@router.get("/api/slide/trajectory/config")
@router.post("/api/slide/trajectory/config")
async def get_trajectory_config():
    return {
        "ok": True,
        "data": {
            "collect_enabled": True,
            "dispatch_enabled": False,
            "max_attempts_per_popup": 5,
            "templates": []
        }
    }
