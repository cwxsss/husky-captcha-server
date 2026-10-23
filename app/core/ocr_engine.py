import base64
import io
import re
from typing import Optional, Tuple
from PIL import Image
import numpy as np

from app.core.math_solver import solve_math_equation

# Global OCR singleton
_ocr_instance = None

def get_ocr_instance():
    global _ocr_instance
    if _ocr_instance is None:
        try:
            import ddddocr
            _ocr_instance = ddddocr.DdddOcr(show_ad=False)
        except Exception as e:
            print(f"[Warning] ddddocr initialization failed or not installed: {e}")
            _ocr_instance = False
    return _ocr_instance if _ocr_instance is not False else None

def clean_base64_data(data_str: str) -> bytes:
    """Removes data URL headers like data:image/png;base64, and returns raw bytes."""
    if not data_str:
        return b""
    s = data_str.strip()
    if "," in s and (s.startswith("data:") or "base64," in s):
        s = s.split(",", 1)[1]
    # Remove any whitespaces/newlines
    s = re.sub(r"\s+", "", s)
    return base64.b64decode(s)

def preprocess_image_bytes(raw_bytes: bytes) -> bytes:
    """
    Preprocess image:
    1. If PNG has transparent alpha channel, blend over solid white background.
    2. Convert to standard RGB/Grayscale.
    """
    try:
        image = Image.open(io.BytesIO(raw_bytes))
        if image.mode in ("RGBA", "LA") or (image.mode == "P" and "transparency" in image.info):
            # Alpha composite onto solid white background
            alpha = image.convert("RGBA")
            bg = Image.new("RGBA", alpha.size, (255, 255, 255, 255))
            blended = Image.alpha_composite(bg, alpha).convert("RGB")
            out_buf = io.BytesIO()
            blended.save(out_buf, format="JPEG", quality=95)
            return out_buf.getvalue()
        return raw_bytes
    except Exception:
        return raw_bytes

def recognize_captcha(image_b64: str, captcha_type: str = "general") -> Tuple[str, dict]:
    """
    Performs OCR recognition on the input base64 image.
    Supports general, numeric, chinese, and math calculation captcha.
    Returns: (recognized_value, metadata)
    """
    raw_bytes = clean_base64_data(image_b64)
    if not raw_bytes:
        return "", {"error": "EMPTY_IMAGE"}
        
    cleaned_bytes = preprocess_image_bytes(raw_bytes)
    ocr = get_ocr_instance()
    
    recognized_text = ""
    if ocr is not None:
        try:
            recognized_text = ocr.classification(cleaned_bytes)
        except Exception as e:
            return "", {"error": f"OCR_ERROR: {str(e)}"}
    else:
        # Fallback if ddddocr is not available in environment
        return "1234", {"warning": "DDDDOCR_NOT_INITIALIZED_MOCK"}
        
    # Check if arithmetic calculation is requested or detected
    math_result = solve_math_equation(recognized_text)
    final_value = recognized_text
    
    if captcha_type == "math":
        if math_result is not None:
            final_value = math_result
    else:
        # If text clearly looks like a math problem like 3+5=?, compute it automatically
        if math_result is not None and any(c in recognized_text for c in ["+", "-", "*", "x", "X", "=", "等于"]):
            final_value = math_result

    # Post cleanup for numeric
    if captcha_type == "numeric":
        digits = re.sub(r"\D+", "", final_value)
        if digits:
            final_value = digits

    return final_value, {
        "raw_text": recognized_text,
        "math_solved": math_result is not None,
        "type": captcha_type
    }
