import json
from pathlib import Path
from typing import Optional


def load_cookie_local(file_path: str = "api/cookies.local.json") -> Optional[str]:
    """从本地文件读取 Cookie 字符串并返回（只做读取与封装，保持最简）。

    支持两种格式：
    1）原始 Cookie 头（推荐，完全复刻浏览器）：
        {"Cookie": "a=b; c=d; ..."}

    2）Cookie 字典（你当前 cookies.local.json 的格式）：
        {"请求 Cookie": {"a": "b", "c": "d"}}

    说明：
    - 该文件建议只放本机，并已在 .gitignore 中忽略
    - 文件不存在时返回 None（表示不带 Cookie 请求）
    """

    p = Path(file_path)
    if not p.exists():
        return None

    raw = json.loads(p.read_text(encoding="utf-8"))
    if not isinstance(raw, dict):
        raise TypeError("cookies.local.json 格式不正确，必须是 JSON 对象")

    cookie_header = raw.get("Cookie")
    if isinstance(cookie_header, str) and cookie_header.strip():
        return cookie_header.strip()

    cookie_dict = raw.get("请求 Cookie")
    if isinstance(cookie_dict, dict):
        parts: list[str] = []
        for k, v in cookie_dict.items():
            if v is None:
                continue
            parts.append(f"{k}={v}")
        return "; ".join(parts) if parts else None

    return None


# 兼容旧函数名（如果你其他脚本已写死 _load_cookie_local）
_load_cookie_local = load_cookie_local
