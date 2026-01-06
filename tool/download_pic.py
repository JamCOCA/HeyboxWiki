from __future__ import annotations

import os
import re
from pathlib import Path
from urllib.parse import urlparse

import requests


def _safe_filename(name: str, *, fallback: str = "image") -> str:
	name = (name or "").strip()
	name = re.sub(r"[\\/:*?\"<>|]+", "_", name)  # Windows 不允许的字符
	name = re.sub(r"\s+", " ", name).strip(" .")
	return name or fallback


def _infer_ext_from_url(url: str) -> str:
	path = urlparse(url).path
	suffix = Path(path).suffix.lower()
	# 只接受常见图片后缀，避免把 .php/.aspx 之类当成图片
	if suffix in {".png", ".jpg", ".jpeg", ".gif", ".webp", ".bmp", ".svg"}:
		return suffix
	return ".png"


def _dedupe_path(path: Path) -> Path:
	if not path.exists():
		return path
	stem, suffix = path.stem, path.suffix
	for i in range(1, 10_000):
		candidate = path.with_name(f"{stem}_{i}{suffix}")
		if not candidate.exists():
			return candidate
	raise FileExistsError(f"无法生成不冲突的文件名：{path}")



def download_image(
	url: str,
	save_dir: str | os.PathLike[str],
	*,
	timeout_s: float = 30.0,
	retries: int = 3,
	chunk_size: int = 256 * 1024,
	user_agent: str = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Safari/537.36",
) -> str:
	"""最简单的直接下载图片。

	参数:
		url: 图片地址（直链）
		save_dir: 保存到本地的目录（不存在会自动创建）

	可选:
		timeout_s: 超时秒数
		retries: 失败重试次数
		chunk_size: 流式写入的块大小

	返回:
		保存后的本地文件绝对路径（str）
	"""
	save_root = Path(save_dir)
	save_root.mkdir(parents=True, exist_ok=True)

	headers = {
		"User-Agent": user_agent,
		"Accept": "image/avif,image/webp,image/apng,image/*,*/*;q=0.8",
		"Referer": url,
	}

	session = requests.Session()
	last_exc: Exception | None = None

	for attempt in range(1, max(1, retries) + 1):
		try:
			with session.get(url, headers=headers, stream=True, timeout=timeout_s, allow_redirects=True) as r:
				r.raise_for_status()

				# 文件名优先取 Content-Disposition，其次取 URL 的 path
				filename = ""
				cd = r.headers.get("Content-Disposition", "")
				m = re.search(r"filename\*=UTF-8''([^;]+)", cd)
				if m:
					filename = requests.utils.unquote(m.group(1))
				else:
					m2 = re.search(r'filename="?([^";]+)"?', cd)
					if m2:
						filename = m2.group(1)

				if filename:
					filename = _safe_filename(filename)
				else:
					ext = _infer_ext_from_url(r.url)
					stem = _safe_filename(Path(urlparse(r.url).path).stem, fallback="image")
					filename = stem + ext

				dst = _dedupe_path(save_root / filename)

				with open(dst, "wb") as f:
					for chunk in r.iter_content(chunk_size=chunk_size):
						if chunk:
							f.write(chunk)

				return str(dst.resolve())
		except Exception as e:
			last_exc = e
			if attempt >= max(1, retries):
				raise

	# 理论上不会走到这里
	if last_exc is not None:
		raise last_exc
	raise RuntimeError("download_image: 未知错误")


if __name__ == "__main__":
	# 例子：可以替换为任意图片直链或需要浏览器才能拿到的地址
	out = download_image(
		"https://cdn.poedb.tw/image/Art/2DItems/Currency/CurrencyIdentification.webp",
		"Artwork/Icon/webp",
	)
	print(out)

