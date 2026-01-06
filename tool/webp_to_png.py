from __future__ import annotations

import os
from pathlib import Path
from typing import Union


PathLike = Union[str, os.PathLike]


def convert_webp_to_png(webp_path: PathLike, output_dir: PathLike) -> str:
	"""将 WebP 转换为 PNG，保留透明通道。

	参数：
		webp_path: 输入 webp 文件路径
		output_dir: 输出目录（会在此目录下生成同名 .png）

	返回：
		输出 png 的绝对路径（字符串）

	说明：
		- 若 webp 包含 alpha，会以 RGBA 保存。
		- 若不包含 alpha，会以 RGB 保存。
		- 会自动创建输出目录。
	"""

	webp_path = Path(webp_path)
	output_dir = Path(output_dir)

	if not webp_path.exists():
		raise FileNotFoundError(f"输入文件不存在: {webp_path}")

	output_dir.mkdir(parents=True, exist_ok=True)
	output_png_path = output_dir / f"{webp_path.stem}.png"

	try:
		from PIL import Image
	except ImportError as e:
		raise ImportError(
			"缺少依赖 Pillow，请先安装：pip install Pillow"
		) from e

	# 打开 WebP
	with Image.open(webp_path) as im:
		# 有些 WebP 会是 P 模式/LA 等，这里统一转换以确保保存时带 alpha
		has_alpha = (
			(im.mode in ("RGBA", "LA"))
			or ("transparency" in getattr(im, "info", {}))
		)
		im_converted = im.convert("RGBA" if has_alpha else "RGB")
		im_converted.save(output_png_path, format="PNG")

	return str(output_png_path.resolve())



if __name__ == "__main__":
	# Windows 路径建议用 Path 或 raw string，避免反斜杠转义
	out = convert_webp_to_png(
		"Artwork/Icon/webp/CurrencyIdentification.webp",
		"Artwork/Icon/png",
	)
	print(out)
