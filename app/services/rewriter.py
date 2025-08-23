# app/services/rewriter.py
import re
from typing import Dict, Any

def _cleanup(s: str) -> str:
    s = re.sub(r"\s+", " ", s).strip()
    s = s.replace(" ,", ",").replace(" .", ".")
    return s

def propose_rewrite_strict(original: str, issue_message: str = "", policy: Dict[str, Any] | None = None) -> str:
    """
    Minimal, deterministic active-voice & clarity rewriter.
    Works even if policy is None. Keeps a colon if the sentence is introducing a figure/list.
    """
    if not original:
        return ""
    text = original.strip()

    # Keep trailing colon if it looks like an intro
    keep_colon = text.rstrip().endswith(":")
    base = text.rstrip(": ").strip()

    # 1) Normalize some common passives
    # e.g., "X is/was/are/were <pp>" -> "The system <verb> X"
    # Specific: "is displayed" -> "shows"/"displays"
    repls = [
        (r"\bis displayed\b", "shows"),
        (r"\bare displayed\b", "show"),
        (r"\bis shown\b", "shows"),
        (r"\bare shown\b", "show"),
        (r"\bis generated\b", "generates"),
        (r"\bare generated\b", "generate"),
        (r"\bis created\b", "creates"),
        (r"\bare created\b", "create"),
        (r"\bis uploaded\b", "uploads"),
        (r"\bare uploaded\b", "upload"),
        (r"\bis updated\b", "updates"),
        (r"\bare updated\b", "update"),
        (r"\bis configured\b", "configures"),
        (r"\bare configured\b", "configure"),
        (r"\bcannot be\b", "can’t be"),
    ]
    s = " " + base + " "
    for pat, verb in repls:
        s = re.sub(pat, verb, s, flags=re.IGNORECASE)

    s = s.strip()

    # 2) Heuristic: “Once X is created and Y uploaded, you can …”
    #   -> “After you create X and upload Y, …”
    m = re.match(
        r'(?i)\s*once\s+(.*?)\s*,\s*you can\s+(.*)',
        s
    )
    if m:
        pre, action = m.group(1).strip(), m.group(2).strip()
        # turn “…mapping is created and images uploaded” -> “you create the mapping and upload the images”
        pre = re.sub(r"\b(\w+)\s+is\s+(\w+?ed)\b", r"you \2 \1", pre, flags=re.IGNORECASE)
        pre = re.sub(r"\b(\w+)\s+are\s+(\w+?ed)\b", r"you \2 \1", pre, flags=re.IGNORECASE)
        pre = re.sub(r"\bimages uploaded\b", "you upload the images", pre, flags=re.IGNORECASE)
        pre = re.sub(r"\bmapping created\b", "you create the mapping", pre, flags=re.IGNORECASE)
        pre = re.sub(r"\bstatus mapping\b", "status mapping", pre, flags=re.IGNORECASE)

        # “through Asset configuration page” -> “on the Asset Configuration page”
        action = re.sub(r"(?i)\bthrough\b\s+asset configuration page", "on the Asset Configuration page", action)
        action = re.sub(r"(?i)\bthrough\b\s+the asset configuration page", "on the Asset Configuration page", action)

        s = f"After {pre}, {action}"
    else:
        # Another common pattern: “Once X is created …” without “you can”
        s = re.sub(r"(?i)^once\s+", "After ", s)

    # 3) Minor clarity tweaks
    s = re.sub(r"(?i)\bassign it to\b", "assign it to", s)
    s = re.sub(r"(?i)\bcorresponding assets\b", "the corresponding assets", s)

    s = _cleanup(s)
    if keep_colon and not s.endswith(":"):
        s += ":"
    return s
