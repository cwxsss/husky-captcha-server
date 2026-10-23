from fastapi import APIRouter, Request

router = APIRouter()

@router.post("/api/userscript/events")
async def handle_userscript_events(request: Request):
    """Batch user event logger."""
    return {
        "ok": True,
        "data": {
            "accepted": True,
            "acceptedCount": 40,
            "responses": []
        }
    }

@router.post("/api/slide/trajectory/report")
async def handle_trajectory_report(request: Request):
    return {"ok": True, "data": {"saved": True}}

@router.post("/api/slide/human-sample/report")
async def handle_human_sample_report(request: Request):
    return {"ok": True, "data": {"saved": True}}

@router.post("/api/userscript/trace-upload")
async def handle_trace_upload(request: Request):
    return {"ok": True, "data": {"saved": True}}

@router.post("/api/normal/shared-binding/report")
@router.post("/api/normal/shared-binding/event")
@router.post("/api/slide/shared-binding/report")
@router.post("/api/slide/shared-binding/event")
async def handle_shared_binding_events(request: Request):
    return {"ok": True, "data": {"saved": True}}
