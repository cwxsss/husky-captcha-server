import re
from typing import Optional

CHINESE_DIGITS = {
    "零": 0, "〇": 0, "一": 1, "二": 2, "两": 2, "三": 3, "四": 4, "五": 5,
    "六": 6, "七": 7, "八": 8, "九": 9, "十": 10
}

OPERATORS = {
    "+": "+", "加": "+", "plus": "+",
    "-": "-", "减": "-", "minus": "-",
    "x": "*", "X": "*", "*": "*", "乘": "*", "times": "*",
    "/": "/", "÷": "/", "除": "/"
}

def solve_math_equation(ocr_text: str) -> Optional[str]:
    """
    Attempts to parse text as a math equation (e.g. '3+5=?', '8*4', '七加五等于几').
    Returns stringified numeric result, or None if not an arithmetic equation.
    """
    if not ocr_text:
        return None
        
    s = ocr_text.strip()
    
    # Check if there is an arithmetic operator
    has_op = any(op in s for op in ["+", "-", "*", "/", "x", "X", "÷", "加", "减", "乘", "除"])
    if not has_op:
        return None
        
    # Replace Chinese numerals with arabic digits
    for k, v in CHINESE_DIGITS.items():
        s = s.replace(k, str(v))
        
    # Standardize operators
    for k, v in OPERATORS.items():
        s = s.replace(k, f" {v} ")
        
    # Remove noise characters
    s = re.sub(r"[=?？等于几结果是多少_#\s]+", " ", s).strip()
    
    # Match pattern: number operator number
    m = re.search(r"(\d+)\s*([+\-*/])\s*(\d+)", s)
    if not m:
        return None
        
    try:
        a = int(m.group(1))
        op = m.group(2)
        b = int(m.group(3))
        
        if op == "+":
            return str(a + b)
        elif op == "-":
            return str(a - b)
        elif op == "*":
            return str(a * b)
        elif op == "/":
            return str(a // b if b != 0 else 0)
    except Exception:
        pass
        
    return None
