import io
from typing import Tuple, Dict, Any, Optional
import numpy as np
from PIL import Image

from app.core.ocr_engine import clean_base64_data

_slide_det_instance = None

def get_slide_det_instance():
    global _slide_det_instance
    if _slide_det_instance is None:
        try:
            import ddddocr
            _slide_det_instance = ddddocr.DdddOcr(det=False, ocr=False, show_ad=False)
        except Exception as e:
            print(f"[Warning] ddddocr slide detector initialization failed: {e}")
            _slide_det_instance = False
    return _slide_det_instance if _slide_det_instance is not False else None

def opencv_match_slide(bg_bytes: bytes, target_bytes: bytes) -> Optional[Tuple[int, int]]:
    """
    Fallback slider matching using OpenCV edge detection and template matching.
    """
    try:
        import cv2
        bg_np = np.frombuffer(bg_bytes, np.uint8)
        bg_img = cv2.imdecode(bg_np, cv2.IMREAD_UNCHANGED)
        
        target_np = np.frombuffer(target_bytes, np.uint8)
        target_img = cv2.imdecode(target_np, cv2.IMREAD_UNCHANGED)
        
        if bg_img is None or target_img is None:
            return None
            
        # Extract alpha mask if available
        mask = None
        if len(target_img.shape) == 3 and target_img.shape[2] == 4:
            alpha = target_img[:, :, 3]
            _, mask = cv2.threshold(alpha, 128, 255, cv2.THRESH_BINARY)
            target_bgr = cv2.cvtColor(target_img, cv2.COLOR_BGRA2BGR)
        else:
            target_bgr = target_img
            
        bg_bgr = cv2.cvtColor(bg_img, cv2.COLOR_BGRA2BGR) if len(bg_img.shape) == 3 and bg_img.shape[2] == 4 else bg_img
        
        # Canny edge detection
        bg_gray = cv2.cvtColor(bg_bgr, cv2.COLOR_BGR2GRAY)
        target_gray = cv2.cvtColor(target_bgr, cv2.COLOR_BGR2GRAY)
        
        bg_canny = cv2.Canny(bg_gray, 100, 200)
        target_canny = cv2.Canny(target_gray, 100, 200)
        
        # Match template
        res = cv2.matchTemplate(bg_canny, target_canny, cv2.TM_CCOEFF_NORMED)
        min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res)
        x, y = max_loc
        return int(x), int(y)
    except Exception as e:
        print(f"[OpenCV slide match error]: {e}")
        return None

def solve_slide(
    bg_b64: str,
    target_b64: str,
    bg_display_width: float = 0,
    target_display_width: float = 0
) -> Dict[str, Any]:
    """
    Solves slide jigsaw puzzle offset.
    Returns:
    {
        "target": [x, y],
        "distance": x,
        "raw_x": x,
        "method": "ddddocr" | "opencv"
    }
    """
    bg_bytes = clean_base64_data(bg_b64)
    target_bytes = clean_base64_data(target_b64)
    
    if not bg_bytes:
        return {"error": "EMPTY_BACKGROUND"}
        
    actual_width = 0
    actual_height = 0
    try:
        with Image.open(io.BytesIO(bg_bytes)) as im:
            actual_width, actual_height = im.size
    except Exception:
        pass
        
    x = 0
    y = 0
    used_method = "ddddocr"
    
    # 1. Try ddddocr slide_match first
    slide_det = get_slide_det_instance()
    if slide_det is not None and target_bytes:
        try:
            res = slide_det.slide_match(target_bytes, bg_bytes, simple_target=True)
            if res and "target" in res:
                # res['target'] = [x1, y1, x2, y2]
                x = res["target"][0]
                y = res.get("target_y", res["target"][1])
        except Exception:
            x = 0
            
    # 2. If ddddocr failed or returned 0, try OpenCV template matching
    if x <= 0 and target_bytes:
        cv_res = opencv_match_slide(bg_bytes, target_bytes)
        if cv_res:
            x, y = cv_res
            used_method = "opencv"
            
    # Apply display scaling if frontend passed different display size
    final_x = x
    if bg_display_width > 0 and actual_width > 0 and abs(bg_display_width - actual_width) > 1:
        scale = bg_display_width / actual_width
        final_x = round(x * scale, 2)
        
    return {
        "target": [final_x, y],
        "distance": final_x,
        "raw_x": x,
        "raw_y": y,
        "actual_width": actual_width,
        "method": used_method
    }
