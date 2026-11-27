from datetime import datetime, timezone
from typing import Any, Dict, Optional


def response_success(data: Any = None, meta: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    meta = meta or {}
    meta.setdefault("timestamp", datetime.now(timezone.utc).isoformat())
    return {"success": True, "data": data, "meta": meta}


def response_error(code: str, message: str, details: Optional[list] = None, meta: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    meta = meta or {}
    meta.setdefault("timestamp", datetime.now(timezone.utc).isoformat())
    return {
        "success": False,
        "error": {"code": code, "message": message, "details": details or []},
        "meta": meta,
    }
