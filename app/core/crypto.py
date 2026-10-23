import base64
import json
import time
import random
from typing import Any, Dict, Optional, Tuple

MASK_SALT = "ctw_2026_slide_mask_v1"

def fnv1a32(text: str) -> int:
    """FNV-1a 32-bit hash implementation matching JavaScript userscript."""
    h = 2166136261
    for byte in text.encode("utf-8"):
        h = ((h ^ byte) * 16777619) & 0xFFFFFFFF
    return h

def xorshift32(seed: int) -> int:
    """Xorshift 32-bit PRNG matching JavaScript userscript."""
    y = seed & 0xFFFFFFFF
    y = (y ^ ((y << 13) & 0xFFFFFFFF)) & 0xFFFFFFFF
    y = (y ^ (y >> 17)) & 0xFFFFFFFF
    y = (y ^ ((y << 5) & 0xFFFFFFFF)) & 0xFFFFFFFF
    return y & 0xFFFFFFFF

def decrypt_protected_payload(protected_data: Dict[str, Any]) -> Tuple[bool, Any]:
    """
    Decrypts protected payload sent by Tampermonkey client:
    {
        "v": 1,
        "alg": "fnv1a32-xorshift32",
        "nonce": "...",
        "payload": "..." (base64)
    }
    """
    if not isinstance(protected_data, dict):
        return False, None
    nonce = str(protected_data.get("nonce") or "")
    payload_b64 = str(protected_data.get("payload") or "")
    if not nonce or not payload_b64:
        return False, None
    try:
        raw_bytes = base64.b64decode(payload_b64)
        seed = fnv1a32(f"{MASK_SALT}|{nonce}") or 2779096485
        out = bytearray(len(raw_bytes))
        for i in range(len(raw_bytes)):
            seed = xorshift32(seed)
            out[i] = raw_bytes[i] ^ (seed & 0xFF)
        text = out.decode("utf-8")
        return True, json.loads(text)
    except Exception:
        return False, None

def encrypt_response_payload(data: Any) -> Dict[str, Any]:
    """
    Optionally encrypts response data in the protected envelope format.
    """
    try:
        raw_bytes = json.dumps(data, ensure_ascii=False).encode("utf-8")
        nonce = f"{int(time.time()*1000):x}{random.randint(100000, 999999):x}"[:16]
        seed = fnv1a32(f"{MASK_SALT}|{nonce}") or 2779096485
        out = bytearray(len(raw_bytes))
        for i in range(len(raw_bytes)):
            seed = xorshift32(seed)
            out[i] = raw_bytes[i] ^ (seed & 0xFF)
        payload_b64 = base64.b64encode(out).decode("utf-8")
        return {
            "v": 1,
            "alg": "fnv1a32-xorshift32",
            "nonce": nonce,
            "payload": payload_b64
        }
    except Exception:
        return {}
